# coding: utf-8
# Script that goes onto eclass and crowdmark.
# Then Checks vs old data, and saves to excel
# This Script test if web can go direct to each grade id, bypassing the need for stupid grade click.
# Less need to change
# Maybe add percent sign after alignments

# Import variables
import selenium
from selenium.webdriver.common.by import By  # For wait until find 'by' condition
from selenium.webdriver.support.ui import WebDriverWait  # Wait condition
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options

import math
import os
import sys
from datetime import date

from LogClear import email
import Log
import logging

# todo rem total, add weekday to main

# Global Variables
# locations
os.chdir(os.path.dirname(sys.argv[0]))
de_link = 'https://eclass.srv.ualberta.ca/my/'  # default link
web_link = 'https://eclass.srv.ualberta.ca/grade/report/user/index.php?id='  # To change courses base on ID
crowd_link = 'https://app.crowdmark.com/student/courses/'  # Link for crowdmark courses
log_name = 'log.log'
csv_file = 'Grades.csv'  # File location of Spreadsheet

# users & passwords
# users & passwords opens file then saves them
usr_f = open('UsrInfo.txt', 'r')
lines = usr_f.readlines()
usr = str(lines[2]).strip()
psw = str(lines[4]).strip()
c_usr = str(lines[6]).strip()  # crowdmark usr
c_psw = str(lines[8]).strip()  # crowdmark password

# for email credentials
user = str(lines[10]).strip()
password = str(lines[14]).strip()
receivers = str(lines[12]).strip().split(', ')
usr_f.close()

# Course list to call function
course_id = {'CIV E 270 Lec': '63547', 'CIV E 270 Lab': '64807', 'CH E 243 Lec': '62226', 'Ch E 243 Sem': '64632',
             'ENGG 299': '64113', 'MATH 209 Lec': '63051', 'MATH 209 Lab': '635311', 'MEC E 200': '64082',
             'MEC E 250': '64397', 'STAT 235 Lec': '63953', 'STAT 235 Lab': '64115'}
crowd_course = {}  # if crowdmark

# What to print if not marked
not_marked = "N M"
not_marked_yet = "Not M Yet"

# Dictionaries for Holding grade and percentage outputs
dict_grades = {}
dic_out_of = {}
dict_percent = {}
old_percent = {}

# list of all courses with changed dict_percent
changed_course = {}

# initialize the log settings
logging.basicConfig(filename=log_name, level=logging.INFO)
was_error = False  # any errors
attachment = []  # files to attach

# Define driver
options = Options()
options.headless = True

weekday = date.today().weekday()  # gets current date to clear log
e_sub = 'Changed Grades'
sub = e_sub

# Functions
# grades per course
class CourseGrades:
    def __init__(self, co):
        self.ass_names = []
        self.grade = []
        self.possible = []
        self.percent = []
        self.mod = 2
        self.course = co
        self.old_g_ls = []

    # Removes redundant dict_percent for specific courses.
    def format_course(self):
        """Used to remove other values from dicts if eclass has different format.

        """
        # only adds final dict_percent from lab
        if self.course == 'CIV E 270 Lec':
            for ass_num in range(len(self.possible)):

                # Only takes third grade
                if (ass_num + 1) != 1 and ass_num % 3 != 0:  # since index is zero; only keep 1 of each ass
                    self.grade[ass_num] = "$"  # Value that can be removed
                    self.possible[ass_num] = "$"

        # Only adds midterm dict_percent
        elif self.course == 'CIV E 270 Lab':
            ass_l = []
            for ass_num in range(len(self.possible)):
                el = 'Section D1 - LABORATORY NO.{} SUBMISSION PORTAL'.format(ass_num + 1)
                sec_d1 = driver.find_elements_by_tag_name('a')  # test if there is a link with ass_num
                for d in sec_d1:
                    d = d.text
                    ass_l.append(d)
                if el not in sec_d1:  # if not a link
                    self.grade[ass_num] = "$"  # Value that can be removed
                    self.possible[ass_num] = "$"

        elif self.course == 'MEC E 200':
            for ass_num in range(len(self.possible)):
                try:
                    float(self.possible[ass_num])  # test if float
                except ValueError:
                    self.grade[ass_num] = "$"  # Value that can be removed
                    self.possible[ass_num] = "$"

        elif self.course == 'STAT 235 Lec':  # Not Working yet
            for ass_num in range(len(self.possible)):
                if ass_num + 1 == 6 or ass_num + 1 == 12 or ass_num + 1 > 15:  # to remove assign total
                    self.grade[ass_num] = "$"  # Value that can be removed
                    self.possible[ass_num] = "$"
        if '$' in self.grade:  # removes the extra superfluous dict_percent
            self.grade.remove('$')
            self.possible.remove('$')

    # Finding Grades
    # Change To find column: ie change empty variables
    def find_grades(self):
        ind = 0  # Increments evey data row
        rmv_feedback = 0

        # Finds Table data points
        li = driver.find_elements_by_tag_name('td')
        for g in li:
            g = g.text

            # Removes text for feedback column
            if len(g) >= 1:
                rmv_feedback += 1
            if rmv_feedback % 3 == 0:
                g = ''

            if g != '' and g != ' ':  # Checks if element is blank
                ind += 1  # Increments indexes only after removing blank

                if ind % self.mod == 0:
                    pos = g.split('–')  # Looks at second value in grade_2 range
                    if len(pos) == 2:  # Only looks if split is viable
                        self.possible.append(pos[1])
                    else:
                        self.possible.append('-')  # Will return not marked in two blocks
                else:
                    self.grade.append(g)

        self.format_course()  # calls function for rand courses
        self.percent_cal()  # calls percent function

    def find_g(self):  # to use if works
        rows = driver.find_elements_by_tag_name('tr')
        header = rows.find_element_by_tag_name('th')
        try:
            header.find_element_by_tag_name('span')
        except:  # todo fix expet, use instead
            pass
        else:
            self.ass_names.append(header)
            data_list = rows.find_elements_by_tag_name('td')

            for col in data_list:
                cl = col.getAttribute('class')
                col_type = cl.split(' ', -1)
                if col_type == 'grade':
                    self.grade.append(col.text)
                elif col_type == 'range':
                    self.possible.append(col.text)

    # Percentage calculation
    def percent_cal(self):
        ass_len = len(self.possible) - 1  # Number of assignments

        try:
            if ass_len == 0:  # so range works when only one assignment
                if self.possible[0] == '' or self.possible[0] == '-':
                    self.possible[0] = not_marked
                else:
                    # Returns "Not marked" unless a value is given.
                    # Else calculates percent for that assignment
                    if self.grade[0] == '-' or self.grade[0] == '-':
                        self.grade[0] = not_marked_yet
                        self.percent.append(self.grade[0])

                    elif self.possible[0] != '$' and self.grade[0] != '$':
                        per = str((float(self.grade[0]) / float(self.possible[0])) * 100)
                        self.percent.append(per)

        except ValueError as er:
            logging.exception('Error in percentage, class: {}, assignment:{}, error{}'.format(self, '1', er))

        else:
            for cal in range(ass_len):
                try:
                    # Checks if the value is marked
                    if self.possible[cal] == '' or self.possible[cal] == '-':
                        self.possible[cal] = not_marked

                    else:
                        # Returns "Not marked" unless a value is given.
                        # Else calculates percent for that assignment
                        if self.grade[cal] == '-' or self.grade[cal] == '-':
                            self.grade[cal] = not_marked_yet
                            self.percent.append(self.grade[cal])

                        elif self.possible[cal] != '$' and self.grade[cal] != '$':
                            per = str((float(self.grade[cal]) / float(self.possible[cal])) * 100)
                            self.percent.append(per)

                except ValueError as er:
                    logging.exception('Error in percentage, class: {}, assignment:{}, error{}'.format(self, cal, er))

    # Gets dictionary of old courses
    def get_old_percent(self):
        old_grades = old_percent[self.course]
        for g in range(len(old_grades)):
            # Tests if value is a num
            if type(old_grades[g]) == float:

                # Tests if value is a place holder: Nan
                if math.isnan(old_grades[g]):
                    old_grades[g] = "$"  # Replaces with a easy to remove character
                else:
                    old_grades[g] = str(old_grades[g])

            else:
                old_grades[g] = old_grades[g].split("%")

        # Removes characters
        self.old_g_ls = [g for g in old_grades if g != '$']

    # Checks if any dict_percent updated
    def any_updates(self):
        # Two old dict_percent since list of lists need to be removed
        old_grades = []

        # So % can be printed
        cent = "%"

        # Converts to string and saves into final list
        for og in self.old_g_ls:
            if type(og) == str:  # Keeps strings unaltered
                old_grades.append(og)
            else:
                old_grades.append(og[0])

        # Do this if they might be the same
        if len(old_grades) == len(self.grade):

            for i in range(len(old_grades)):

                if old_grades[i] != self.grade[i]:  # Checks if that grade is updated

                    if self.grade[i] == not_marked_yet or self.grade[i] == not_marked or old_grades[i] == not_marked:
                        cent = ''  # Corrects grammar: no % if not marked
                    output_str = "Assignment: {}, Old percentage: {}, New percentage: {}{}".format(str(i + 1),
                                                                                                   old_grades[i],
                                                                                                   self.grade[i],
                                                                                                   cent)
                    if self.course in changed_course.keys():
                        changed_course[self.course].append(output_str)
                    else:
                        changed_course[self.course] = [output_str]

        # They are guaranteed different. Thus print all new indexes
        else:
            # is_same = False
            # Prints the indexes that were not on old index
            dif_len = len(self.grade) - len(old_grades)

            for i in range(dif_len):

                up_in = i + len(old_grades)  # index for new grade
                output_str = "Assignment: {}, New percentage: {}{}".format(str(up_in), self.grade[up_in], cent)

                if self.course in changed_course.keys():
                    changed_course[self.course].append(output_str)
                else:
                    changed_course[self.course] = [output_str]


# main execution
c_l = list(course_id.values())
# todo move to top, csv, log
Log.grab_g()
try:
    logging.info('Logging onto web')
    driver = selenium.webdriver.Chrome(options=options)
    # Logging on
    print('Getting Web Data')
    driver.get(web_link + c_l[0])
    driver.find_element_by_id('username').send_keys(usr)
    driver.find_element_by_id('user_pass').send_keys(psw)
    driver.find_element_by_xpath('/html/body/div/div/div/div/div/form/input[3]').click()
    # Tests if eclass loads
    eclass_load = ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Dashboard"))
    WebDriverWait(driver, 10).until(eclass_load)  # 10 sec max
except Exception as e:
    logging.exception("Error in open web: " + str(e))
    was_error = True

else:  # no error
    # Calls functions for chancing course, and getting dict_percent for each course.
    for c in course_id.keys():
        logging.info('class ' + c)
        try:
            if course_id[c] != c_l[0]:  # Since first link

                g_link = web_link + course_id[c]
                driver.get(g_link)  # Switch courses

            # Saves output as local variable
            course = CourseGrades(c)

            dict_grades[c] = course.grade
            dic_out_of[c] = course.possible
            dict_percent[c] = course.percent

            # Only runs is old dict is updated. Else updates
            # will send message block at end
            if c in old_percent.keys():
                course.get_old_percent()  # Calls up old dict_percent
                course.any_updates()  # True/false for each course

            else:
                changed_course[c] = []

        except ValueError as e:
            logging.exception("error calc" + str(e))
            was_error = True

    driver.quit()  # quits driver

# Excel formatting
try:
    Log.write_grade()
except IOError as e:
    logging.exception("Error in csv: " + str(e))
    was_error = True

# email updates
if weekday == 6:
    sub += ' Weekly Update'
    attachment = [log_name, csv_file]
elif was_error:
    sub += ' Error'
    attachment = [log_name]
if len(changed_course) == 0:
    sub = sub.replace(e_sub, '')

email(sub)
