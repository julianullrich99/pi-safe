import smtplib
import threading

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

def sendmymail(subject1,text):
  mail_user = 'sdrum01@gmail.com'
  mail_pwd = '_01LiquiduM_'
  subject = 'PI-SAFE : ' + subject1
  
  '''
  #Mail parameter
  smtp_server = 'smtp.1und1.de' # 1und1 SMTP Server
  smtp_port = 587
  benutzer = 'xxxxx'
  pwd = 'yyyyyy'
  sender = 'zzzz.de'
  receiver = 'aaa@bbb.de' # mehrer receiver muessen mit ', ' getrennt werden
  subject = 'testtext'
  preambletext = ''
  filepath_selected = "/media/usb/daten/*.png"
  '''
  
  msg = MIMEMultipart()
  msg['From'] = mail_user
  msg['To'] = mail_user
  msg['Subject'] = subject

  msg.attach(MIMEText(text))

  part = MIMEBase('application', 'octet-stream')

  Encoders.encode_base64(part)

  mailServer = smtplib.SMTP("smtp.gmail.com", 587)
  mailServer.ehlo()
  mailServer.starttls()
  mailServer.ehlo()
  mailServer.login(mail_user, mail_pwd)
  mailServer.sendmail(mail_user,mail_user, msg.as_string())
  mailServer.close()
  
  print('Mail sent')
