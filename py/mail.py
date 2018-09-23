import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

def sendmymail(text):
  gmail_user = 'sdrum01@gmail.com'
  gmail_pwd = '_01LiquiduM_'
  subject = 'PI-SAFE Message'


  msg = MIMEMultipart()
  msg['From'] = gmail_user
  msg['To'] = gmail_user
  msg['Subject'] = subject

  msg.attach(MIMEText(text))

  part = MIMEBase('application', 'octet-stream')

  Encoders.encode_base64(part)

  mailServer = smtplib.SMTP("smtp.gmail.com", 587)
  mailServer.ehlo()
  mailServer.starttls()
  mailServer.ehlo()
  mailServer.login(gmail_user, gmail_pwd)
  mailServer.sendmail(gmail_user,gmail_user, msg.as_string())
  mailServer.close()
