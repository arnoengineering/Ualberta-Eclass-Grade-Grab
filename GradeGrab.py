# coding: utf-8
# Script that goes onto eclass and crowdmark.
# Then Checks vs old data, and saves to excel
# This Script test if web can go direct to each grade id, bypassing the need for stupid grade click.

# Import variables
import selenium
from selenium.webdriver.common.by import By  # For wait until find 'by' condition
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait  # Wait condition
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options

import math
import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))

from datetime import date
from GradeGrabMod import *
import logging

# order var, update linux, file-path

# Global Variables
# locations

# initialize the log settings
logging.basicConfig(filename=log_name, level=logging.INFO)
was_error = False  # any errors


# Define driver
options = Options()
options.headless = True

weekday = date.today().weekday()  # gets current date to clear log
sub = e_sub


def loop_crowd():
    # Element locators for wait function
    driver = selenium.webdriver.Chrome(options=options)  # todo add headers
    # crowdmark loading
    driver.get('https://app.crowdmark.com/sign-in')
    driver.find_element_by_id('user_email').send_keys(c_usr)
    driver.find_element_by_id('user_password').send_keys(c_psw)
    driver.find_element_by_xpath('/html/body/section/main/section/div/div[1]/form/div/input').click()

    # Crowdmark calling function
    for cc in crowd_course.keys():  # Grabs id
        crowd = Crowdmark(crowd_course[cc], driver)

        # Reveres Crowdmark's stupid ordering and appends to percent dict
        percent_crowd = crowd.crowd_percent.reverse()
        dict_percent[cc] = percent_crowd

    driver.quit()  # quits driver


def loop_eclass():
    global was_error
    logging.info('Logging onto web')
    driver = selenium.webdriver.Chrome(options=options)
    # Logging on
    print('Getting Web Data')
    driver.get(de_link)
    driver.find_element_by_id('username').send_keys(usr)
    driver.find_element_by_id('user_pass').send_keys(psw)
    driver.find_element_by_xpath('/html/body/div/div/div/div/div/form/input[3]').click()
    # Tests if eclass loads
    eclass_load = ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'eClass'))
    WebDriverWait(driver, 10).until(eclass_load)  # 10 sec max

    # Calls functions for chancing course, and getting dict_percent for each course.
    for c in course_id.keys():
        logging.info('class ' + c)
        try:

            g_link = web_link + course_id[c]
            driver.get(g_link)  # Switch courses

            # Saves output as local variable
            course = CourseGrades(c, driver)

            dict_grades[c] = course.grade
            dic_out_of[c] = course.possible
            dict_percent[c] = course.percent

            # Only runs is old dict is updated. Else updates
            # will send message block at end
            if c in old_percent.keys():
                course.get_old_percent()  # Calls up old dict_percent

            course.any_updates()  # True/false for each course

        except ValueError as er:
            logging.exception("error calc" + str(er))
            was_error = True

    driver.quit()  # quits driver


# Functions
# grades per course
class CourseGrades:
    def __init__(self, co, driver):
        self.ass_names = []
        self.grade = []
        self.possible = []
        self.percent = []
        self.old_g_ls = []

        self.mod = 2
        self.course = co
        self.driver = driver

    # Removes redundant dict_percent for specific courses.
    def format_course(self):
        """Used to remove other values from dicts if eclass has different format.
        head object, will change if not
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
            for ass_num in self.ass_names:
                if not ec.element_to_be_clickable(ass_num):
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

        # sets to text to read
        self.ass_names = [h.text for h in self.ass_names]

    # Finding Grades
    # Change To find column: ie change empty variables
    def find_grades(self):  # to use if works
        rows = self.driver.find_elements_by_tag_name('tr')  # searches for rows then
        for row in rows:
            header = row.find_element_by_tag_name('th')
            try:
                span_el = header.find_element_by_tag_name('span')
            except NoSuchElementException:
                pass
            else:
                if span_el.getAttribute('class') == 'gradeItem':
                    self.ass_names.append(header)
                    data_list = row.find_elements_by_tag_name('td')

                    for col in data_list:
                        cl = col.getAttribute('class')
                        col_type = cl.split(' ', -1)
                        if col_type == 'grade':
                            self.grade.append(col.text)
                        elif col_type == 'range':
                            pos = col.text.split('–')  # Looks at second value in grade_2 range
                            if len(pos) == 2:  # Only looks if split is viable
                                self.possible.append(pos[1])
                            else:
                                self.possible.append('-')  # Will return not marked in two blocks
        self.format_course()  # calls function for rand courses
        self.percent_cal()  # calls percent function

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
                    output_str = "Changed: {}, Old percentage: {}, New percentage: {}{}".format(self.ass_names[i],
                                                                                                old_grades[i],
                                                                                                self.grade[i],
                                                                                                cent)
                    if self.course in changed_course.keys():
                        changed_course[self.course].append(output_str)
                    else:
                        changed_course[self.course] = [output_str]

        # They are guaranteed different. Thus print all new indexes
        else:
            # Prints the indexes that were not on old index
            dif_len = len(self.grade) - len(old_grades)

            for i in range(dif_len):

                up_in = i + len(old_grades)  # index for new grade
                if self.grade[up_in] == not_marked_yet or self.grade[up_in] == not_marked:
                    cent = ''
                output_str = "Changed: {}, New percentage: {}{}".format(self.ass_names[up_in], self.grade[up_in], cent)

                if self.course in changed_course.keys():
                    changed_course[self.course].append(output_str)
                else:
                    changed_course[self.course] = [output_str]


# main execution
LogCSV.grab_g()
try:
    loop_eclass()  # loops though eclass then crowd
    loop_crowd()
except Exception as e:
    logging.exception("Error in open web: " + str(e))
    was_error = True

try:
    LogCSV.write_grade(dict_percent)
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
