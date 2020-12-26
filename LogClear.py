# coding: utf-8
# Removes log file and sends old file if errors
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
weekday = 7  # todo fix

fname = 'log.log'
attachments = [fname, 'Grades.csv']
logging.basicConfig(filename=fname, level=logging.INFO)


def log_check():
    # logging
    c = 0
    with open(fname, 'r') as f:
        for line in f.readlines():
            c += 1
    return c

def log_clear():
    # removes old logs
    file = open(fname, 'w')
    file.truncate(0)
    file.close()


def email(user, receivers, password,  subject, attachment=None, changed_course=None, course_id=None):
    # todo if er: attach

    # format var
    if changed_course is None:
        changed_course = {}
    if course_id is None:
        course_id = {}
    if attachment is None:
        attachment = []

    host_server = "smtp.gmail.com"
    port = 465

    # what to send
    msg = MIMEMultipart()
    msg['To'] = ', '.join(receivers)
    msg['From'] = user
    msg["Subject"] = subject

    def g_mail():
        web_link = ''
        message = 'Grades Changed\n\n'
        links = []
        for d in changed_course.keys():  # loops through every updated course
            message += f"Course Changed: {d}\n"

            # is course in eclass; then loads website
            if d in course_id.keys():
                links.append(web_link + course_id[d])

            # prints new grads
            for m in changed_course[d]:
                message += (m + "\n")

        # adds links to message content
        message += "\nlinks: \n"  # Only prints once tells message box what to say
        for link in links:
            message += (link + "\n")
        return message
    # def main
    if subject == "Grades Changed":
        message_con = g_mail()
    else:
        message_con = f"""{subject}\n\n"""

    if weekday == 7:
        msg['Subject'] += ' Weekly update'
        log = log_check()
    else:
        log = 0
    # sets content
    if log == 0:
        message_con += 'No errors'
        msg.attach(MIMEText(message_con, 'plain'))
    else:
        attachment.append(fname)

    # attachments
    # Open PDF file in binary mode
    for file in attachment:
        with open(file, "rb") as atmnt:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(atmnt.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {file}",)

        # Add attachment to message and convert message to string
        msg.attach(part)

    msg.attach(MIMEText(message_con, 'plain'))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host_server, port, context=ctx) as server:
        server.login(user, password)
        print("starting to send")
        server.sendmail(user, receivers, msg.as_string())
        print("sent")
