# coding: utf-8
# Removes log file and sends old file if errors
import smtplib
import ssl
from email.message import EmailMessage
import logging

usr_f = open('UsrInfo.txt', 'r')
lines = usr_f.readlines()

# for email credentials
user = str(lines[10]).strip()
password = str(lines[14]).strip()
receivers = str(lines[12]).strip().split(',')[0]
usr_f.close()

# logging
c = 0
fname = 'log.log'
with open(fname, 'r') as f:
    for line in f:
        c += 1

logging.basicConfig(filename=fname, level=logging.INFO)

host_server = "smtp.gmail.com"
port = 465

# what to send
msg = EmailMessage()
msg['To'] = receivers
msg['From'] = user
msg["Subject"] = "Log update"

message_con = """Weekly log update\n\n"""


# adds links to message content

# sets content
if c == 0:
    message_con += 'No errors'
    msg.set_content(message_con)
else:
    msg.add_attachment(open("log.log", "r").read())

print(message_con)
print(msg["To"])
print(receivers)
print(user)
print(password)


ctx = ssl.create_default_context()
with smtplib.SMTP_SSL(host_server, port, context=ctx) as server:
    server.login(user, password)
    print("starting to send")
    server.send_message(msg, to_addrs=receivers)
    print("sent")

# removes old logs
file = open(fname, 'w')
file.truncate(0)
file.close()
