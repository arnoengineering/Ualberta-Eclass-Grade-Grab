# coding: utf-8
# Removes log file and sends old file if errors
from GradeGrabMod.Creds import *


import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# checks if lines in log
def log_check():
    with open(log_name, 'r') as f:
        file_len = len(f.readlines())
    return file_len


# removes old logs
def log_clear():
    file = open(log_name, 'w')
    file.truncate(0)
    file.close()


# sends email, adds attachments if sent
def email(subject):

    host_server = "smtp.gmail.com"
    port = 465

    # initializes
    msg = MIMEMultipart()
    msg['To'] = ', '.join(receivers)  # todo change for log
    msg['From'] = user
    msg["Subject"] = subject

    # if grades to be sent, formatting
    def g_mail():
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

    # checks what to send and sends it
    if e_sub in subject:  # used if grades
        message_con = g_mail()
    else:
        message_con = f"""{subject}\n\n"""  # generic message

    # sets content, if check, log will be 0
    if log_name in attachment:
        log = log_check()
        if log == 0:
            attachment.remove(log_name)  # so don't send if empty
            message_con += 'No errors'

    # attachments
    # Open PDF csv_file in binary mode
    for file in attachment:
        with open(file, "rb") as f:
            # Add csv_file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        # Encode csv_file in ASCII characters to send by email
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

    if log_name in attachment:
        log_clear()
