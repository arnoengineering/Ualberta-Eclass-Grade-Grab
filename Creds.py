de_link = 'https://eclass.srv.ualberta.ca/my/'  # default link
web_link = 'https://eclass.srv.ualberta.ca/grade/report/user/index.php?id='  # To change courses base on ID
crowd_link = 'https://app.crowdmark.com/student/courses/'  # Link for crowdmark courses
log_name = 'log.log'
csv_file = 'Grades.csv'  # File location of Spreadsheet
e_sub = 'Changed Grades'


# Course list to call function
course_id = {'CIV E 270 Lec': '63547', 'CIV E 270 Lab': '64807', 'CH E 243 Lec': '62226', 'Ch E 243 Sem': '64632',
             'ENGG 299': '64113', 'MATH 209 Lec': '63051', 'MATH 209 Lab': '635311', 'MEC E 200': '64082',
             'MEC E 250': '64397', 'STAT 235 Lec': '63953', 'STAT 235 Lab': '64115'}
crowd_course = {}  # if crowdmark

attachment = []  # files to attach

# Dictionaries for Holding grade and percentage outputs
dict_grades = {}
dic_out_of = {}
dict_percent = {}
old_percent = {}

# list of all courses with changed dict_percent
changed_course = {}

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
