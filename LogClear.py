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

def log_clear():
    # removes old logs
    file = open(fname, 'w')
    file.truncate(0)
    file.close()


def email(user, receivers, log, attachment, subject):
    host_server = "smtp.gmail.com"
    port = 465

    # what to send
    msg = MIMEMultipart()
    msg['To'] = receivers
    msg['From'] = user
    msg["Subject"] = subject

    message_con = """Weekly log update\n\n"""
    # sets content
    if log == 0:
        message_con += 'No errors'
        msg.attach(MIMEText(message_con, 'plain'))
    else:
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

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host_server, port, context=ctx) as server:
        server.login(user, password)
        print("starting to send")
        server.sendmail(user, receivers, msg.as_string())
        print("sent")
