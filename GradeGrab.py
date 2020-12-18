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

import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
import logging

# Global Variables
# locations
os.chdir(os.path.dirname(sys.argv[0]))
web_link = 'https://eclass.srv.ualberta.ca/grade/report/user/index.php?id='  # To change courses base on ID
file = 'Grades.csv'  # File location of Spreadsheet
crowd_link = 'https://app.crowdmark.com/student/courses/'  # Link for crowdmark courses

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
receivers = str(lines[12]).strip()
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

# list of all courses with changed grades
changed_course = {}

# initialize the log settings
logging.basicConfig(filename='log.log', level=logging.INFO)
was_error = False  # any errors
# Define driver
options = Options()
options.headless = True


# Functions
# Removes redundant grades for specific courses.
def format_course(course, grades, pos):
    # only adds final grades from lab
    if course == 'CIV E 270 Lec':
        for ass_num in range(len(pos)):

            # Only takes third grade
            if (ass_num + 1) != 1 and ass_num % 3 != 0:  # since index is zero; only keep 1 of each ass
                grades[ass_num] = "$"  # Value that can be removed
                pos[ass_num] = "$"

        grades.remove('$')  # removes the extra superfluous grades
        pos.remove('$')

    # Only adds midterm grades
    elif course == 'CIV E 270 Lab':
        ass_l = []
        for ass_num in range(len(pos)):
            el = 'Section D1 - LABORATORY NO.{} SUBMISSION PORTAL'.format(ass_num + 1)
            sec_d1 = driver.find_elements_by_tag_name('a')  # test if there is a link with ass_num
            for d in sec_d1:
                d = d.text
                ass_l.append(d)
            if el not in sec_d1:  # if not a link
                grades[ass_num] = "$"  # Value that can be removed
                pos[ass_num] = "$"
        if '$' in grades:
            grades.remove('$')  # removes the extra superfluous grades
            pos.remove('$')

    elif course == 'MEC E 200':
        for ass_num in range(len(pos)):
            try:
                float(pos[ass_num])  # test if float
            except ValueError:
                grades[ass_num] = "$"  # Value that can be removed
                pos[ass_num] = "$"
        grades.remove('$')  # removes the extra superfluous grades
        pos.remove('$')

    elif course == 'STAT 235 Lec':  # Not Working yet
        for ass_num in range(len(pos)):
            if ass_num + 1 == 6 or ass_num + 1 == 12 or ass_num + 1 > 15:  # to remove assign total
                grades[ass_num] = "$"  # Value that can be removed
                pos[ass_num] = "$"
        grades.remove('$')  # removes the extra superfluous grades
        pos.remove('$')


# Finding Grades
# Change To find column: ie change empty variables
def find_grades(course):
    ind = 0  # Increments evey data row
    rmv_feedback = 0
    possible = []
    grade = []

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

            # Adds out of mark
            if course == 'EN PH 131 LAB':
                mod = 3
            else:
                mod = 2
            if ind % mod == 0:
                pos = g.split('–')  # Looks at second value in grade_2 range
                if len(pos) == 2:  # Only looks if split is viable
                    possible.append(pos[1])
                else:
                    possible.append('-')  # Will return not marked in two blocks
            else:
                grade.append(g)

    format_course(course, grade, possible)  # calls function for rand courses
    percent = percent_cal(course, grade, possible)  # calls percent function
    return grade, possible, percent  # Returns the grades calculated in the function


# Percentage calculation
def percent_cal(course, grade_2, pos2):
    # Local Variables '   ^`^s'
    percent = []
    ass_len = len(pos2) - 1  # Number of assignments

    try:
        if ass_len == 0:  # so range works when only one assignment
            if pos2[0] == '' or pos2[0] == '-':
                pos2[0] = not_marked
            else:
                # Returns "Not marked" unless a value is given.
                # Else calculates percent for that assignment
                if grade_2[0] == '-' or grade_2[0] == '-':
                    grade_2[0] = not_marked_yet
                    per = grade_2[0]
                    percent.append(per)
                elif pos2[0] != '$' and grade_2[0] != '$':
                    per = str((float(grade_2[0]) / float(pos2[0])) * 100)
                    percent.append(per)
    except ValueError as er:
        logging.exception('Error in percentage, class: {}, assignment:{}, error{}'.format(course, '1', str(er)))

    else:
        for cal in range(ass_len):
            try:
                # Checks if the value is marked
                if pos2[cal] == '' or pos2[cal] == '-':
                    pos2[cal] = not_marked

                else:
                    # Returns "Not marked" unless a value is given.
                    # Else calculates percent for that assignment
                    if grade_2[cal] == '-' or grade_2[cal] == '-':
                        grade_2[cal] = not_marked_yet
                        per = grade_2[cal]
                        percent.append(per)
                    elif pos2[cal] != '$' and grade_2[cal] != '$':
                        per = str((float(grade_2[cal]) / float(pos2[cal])) * 100)
                        percent.append(per)
            except ValueError as er:
                logging.exception('Error in percentage, class: {}, assignment:{}, error{}'.format(course, cal, str(er)))

    return percent


# Gets dictionary of old courses
def get_old_percent(course):
    o_course_list = old_percent[course]

    for g in range(len(o_course_list)):
        # Tests if value is a num
        if isinstance(o_course_list[g], float):

            # Tests if value is a place holder: Nan
            if math.isnan(o_course_list[g]):
                o_course_list[g] = "$"  # Replaces with a easy to remove character
            else:
                o_course_list[g] = str(o_course_list[g])

        else:
            o_course_list[g] = o_course_list[g].split("%")

    # Removes characters
    for g in o_course_list[:]:
        if g == "$":
            o_course_list.remove(g)


# Checks if any grades updated
def any_updates(update):
    # Two old grades since list of lists need to be removed
    old_grades = []
    old_grade_temp = old_percent[update]
    new_grade = dict_percent[update]

    # So % can be printed
    cent = "%"

    # Converts to string and saves into final list
    for og in old_grade_temp:
        if isinstance(og, str):  # Keeps strings unaltered
            old_grades.append(og)
        else:
            old_grades.append(og[0])

    # Do this if they might be the same
    if len(old_grades) == len(new_grade):

        for i in range(len(old_grades)):

            if old_grades[i] != new_grade[i]:  # Checks if that grade is updated

                if new_grade[i] == not_marked_yet or new_grade[i] == not_marked or old_grades[i] == not_marked:
                    cent = ''  # Corrects grammar: no % if not marked
                output_str = "Assignment: {}, Old percentage: {}, New percentage: {}{}".format(str(i + 1),
                                                                                               old_grades[i],
                                                                                               new_grade[i],
                                                                                               cent)
                if update in changed_course.keys():
                    changed_course[update].append(output_str)
                else:
                    changed_course[update] = [output_str]

    # They are guaranteed different. Thus print all new indexes
    else:
        # is_same = False
        # Prints the indexes that were not on old index
        dif_len = len(new_grade) - len(old_grades)

        for i in range(dif_len):

            up_in = i + len(old_grades)  # index for new grade
            output_str = "Assignment: {}, New percentage: {}{}".format(str(up_in), new_grade[up_in], cent)

            if update in changed_course.keys():
                changed_course[update].append(output_str)
            else:
                changed_course[update] = [output_str]


# Email Output
def out_put():
    # Google location
    host_server = "smtp.gmail.com"
    port = 465

    # what to send
    msg = EmailMessage()
    msg['From'] = user

    message_con = """Arno your grades have been updated\n\n"""

    links = []

    for d in changed_course.keys():  # loops through every updated course
        message_con += ("Course Changed: " + d + "\n")

        # is course in eclass; then loads website
        if d in course_id.keys():
            links.append(web_link + course_id[d])

        # prints new grads
        for m in changed_course[d]:
            message_con += (m + "\n")

    # adds links to message content
    message_con += "\nlinks: \n"  # Only prints once tells message box what to say
    for lin in links:
        message_con += (lin + "\n")

    # sets content
    if not was_error:
        msg["Subject"] = "Grade Changed"
        msg.set_content(message_con)
        print(message_con)
    else:
        msg["Subject"] = "Grade Error"
        msg.set_content(message_con)
        msg.add_attachment(open("log.log", "r").read())
    logging.info("starting to send")
    print("starting to send")
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(host_server, port, context=ctx) as server:
            server.login(user, password)
            msg['To'] = receivers
            server.send_message(msg)
            print("sent")
    except IOError as er:
        logging.exception("Error in mail: " + str(er))


# Crowdmark function
def crowd():
    # Changes grade column index for crowdmark tests
    def crowd_test(table, mod):  # Mod is modulus

        crowd_percent = []
        ass_crowd = 0  # Number of assignments

        for g in table:  # Changes to text
            g = g.text
            ass_crowd += 1

            if ass_crowd % mod == 0:  # Returns 4th column
                if g != '' and g != '   ^`^t':
                    g_per = g.split("%")  # Removes percent sign
                    crowd_percent.append(g_per[0])
                else:
                    crowd_percent.append(not_marked_yet)

        return crowd_percent

    # Change for course.
    def crowd_change(course):
        # direct link for faster operation
        driver.get(crowd_link + course)
        WebDriverWait(driver, 10).until(g_load)

        # Local Variables
        table_percent = []
        num = 0

        # Changes index for grades if test or assignment
        tables = driver.find_elements_by_tag_name('table')

        if len(tables) == 1:  # Gos directly to assignments if no tests
            data_val = 4
            table_data = tables[0].find_elements_by_tag_name('td')
            table_percent = crowd_test(table_data, data_val)

        else:
            for table_id in tables:  # Looks for table data in each table
                table_data = table_id.find_elements_by_tag_name('td')
                num += 1

                # Goes to tests for first table, and assignments for second.
                if num == 1:
                    data_val = 3

                else:
                    data_val = 4

                # Gets percent from tests then percent from assignments
                crowd_per = crowd_test(table_data, data_val)
                table_percent += crowd_per

        return table_percent

    # Element locators for wait function
    g_load = ec.presence_of_element_located((By.TAG_NAME, 'td'))  # grade tables
    # crowdmark loading
    driver.get('https://app.crowdmark.com/sign-in')
    driver.find_element_by_id('user_email').send_keys(c_usr)
    driver.find_element_by_id('user_password').send_keys(c_psw)
    driver.find_element_by_xpath('/html/body/section/main/section/div/div[1]/form/div/input').click()

    # Crowdmark calling function
    for cc in crowd_course.keys():  # Grabs id
        percent_crowd = crowd_change(crowd_course[cc])

        # Reveres Crowdmark's stupid ordering and appends to percent dict
        percent_crowd.reverse()
        dict_percent[cc] = percent_crowd


# main execution
c_l = list(course_id.values())
try:
    read = pd.read_csv(file)  # read from excel
    if not read.empty:
        print('Logging Grades')
        old_percent = read.to_dict('list')
    for k in old_percent.keys():
        if k not in course_id.keys():
            old_percent.remove(k)
except Exception as e:
    was_error = True
    logging.exception("Error in open csv: " + str(e))

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
    # Calls functions for chancing course, and getting grades for each course.
    for c in course_id.keys():
        logging.info('class' + c)
        try:
            if course_id[c] != c_l[0]:  # Since first link

                g_link = web_link + course_id[c]
                driver.get(g_link)  # Switch courses

            # Saves output as local variable
            course_g, course_o, course_p = find_grades(c)

            dict_grades[c] = course_g
            dic_out_of[c] = course_o
            dict_percent[c] = course_p
        except ValueError as e:
            logging.exception("error calc" + str(e))
            was_error = True

    # Calls function for any updates; for each course
    for co in course_id.keys():

        # Only runs is old dict is updated. Else updates
        # will send message block at end
        if co in old_percent.keys():
            get_old_percent(co)  # Calls up old grades
            any_updates(co)  # True/false for each course

        else:
            changed_course[co] = []
    driver.quit()  # quits driver

# Excel formatting
# Padding the dicts so that all are same length to print
lmax = 0

# Finds longest list of grades
for n in dict_percent.keys():
    lmax = max(lmax, len(dict_percent[n]))

# Sets all other courses to have same length: with empty str
for n in dict_percent.keys():
    leng = len(dict_percent[n])

    if leng < lmax:
        dict_percent[n] += [""] * (lmax - leng)
try:
    # Outputs to file
    df = pd.DataFrame(data=dict_percent)  # Selects Data
    df.to_csv(file, index=False)
except IOError as e:
    logging.exception("Error in csv: " + str(e))
    was_error = True

# email updates
if len(changed_course) != 0 or was_error:
    out_put()
else:
    print('Nothing Updated')