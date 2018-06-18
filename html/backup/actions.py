import RPi.GPIO as GPIO
from picamera import PiCamera
import base64
from common import *
import time
import json
import os, sys, sqlite3

dbfile  = "/var/www/db/misafe.db"
state = 0

# from __main__ import clients
#GPIO.setmode(GPIO.BCM)

def sendToClients(arr):
  for client in clients:
    client.sendMessage(u""+json.dumps(arr))

def dbconnect():
    global dbfile
    if not os.path.exists(dbfile):
      print "DB misafe.db doesn't exists - DB will be created."
      create_db()


def create_db():
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    # Tabelle user erzeugen
    sql = 'CREATE TABLE user(id INTEGER, pin1 INTEGER, pin2 INTEGER)'
    cursor.execute(sql)
    sql = "INSERT INTO user VALUES(" + str(1) + ", "+ str(1234) + ", "+str(1234)+")"
    cursor.execute(sql)
    con.commit()
    
    # Tabelle user erzeugen
    sql = 'CREATE TABLE colors(id INTEGER, id_user INTEGER, r1 INTEGER, g1 INTEGER, b1 INTEGER, r2 INTEGER, g2 INTEGER, b2 INTEGER)'
    cursor.execute(sql)
    sql = "INSERT INTO colors (id,id_user,r1,g1,b1,r2,g2,b2)VALUES(1,1,255,0,255,255,255,0)"
    cursor.execute(sql)
    con.commit()
    
    con.close()
    print "Datenbank "+dbfile+" mit ", sql ," Inhalt angelegt"

def get_password(user):
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "SELECT * FROM user WHERE id = "+ str(user)
    cursor.execute(sql)
    for data in cursor:
        pw1 = data[1]
        pw2 = data[2]

    con.close()
    return (pw1)

def change_password(user,newpin):
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "UPDATE user SET pin1 = "+str(newpin)+" WHERE id = "+ str(user)
    cursor.execute(sql)
    con.commit()
    con.close()
    return (1)

def store_rgb(user,which,rgb):
    global dbfile
    w = str(which)
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "UPDATE colors SET "
    sql += "r"+w+" = "+str(rgb['r'])+", "
    sql += "g"+w+" = "+str(rgb['g'])+", "
    sql += "b"+w+" = "+str(rgb['b'])+" "
    sql += "WHERE id = 1"
    print sql
    cursor.execute(sql)
    con.commit()
    con.close()
    return (1)
    
def get_rgb():
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "SELECT * FROM colors WHERE id = 1"
    cursor.execute(sql)
    
    for data in cursor:
      r1 = data[2]
      g1 = data[3]
      b1 = data[4]
      r2 = data[5]
      g2 = data[6]
      b2 = data[7]
    arr = {"r1":r1,"g1":g1,"b1":b1,"r2":r2,"g2":g2,"b2":b2}
    con.close()
    return (arr)

class actions:
    def __init__(self):
        dbconnect()
        self.camera = PiCamera()
        
        arr_rgb = get_rgb()
        print("Color initialisation:")
        print("RGB1: " + str(arr_rgb["r1"])+ " " + str(arr_rgb["g1"])+ " " + str(arr_rgb["b1"]))
        print("RGB2: " + str(arr_rgb["r2"])+ " " + str(arr_rgb["g2"])+ " " + str(arr_rgb["b2"]))

        
        #GPIO.setWarnings(false)
        GPIO.setup(5, GPIO.OUT) #R1
        GPIO.setup(6, GPIO.OUT) #G1
        GPIO.setup(13, GPIO.OUT)#B1
        self.r1 = GPIO.PWM(5, 100) #Pin, Frequency
        self.g1 = GPIO.PWM(6, 100)
        self.b1 = GPIO.PWM(13, 100)
        self.r1.start(arr_rgb["r1"]*100/255)
        self.g1.start(arr_rgb["g1"]*100/255)
        self.b1.start(arr_rgb["b1"]*100/255)
        
        GPIO.setup(17, GPIO.OUT)#R2
        GPIO.setup(18, GPIO.OUT)#G2
        GPIO.setup(27, GPIO.OUT)#B2
        self.r2 = GPIO.PWM(17, 100)
        self.g2 = GPIO.PWM(18, 100)
        self.b2 = GPIO.PWM(27, 100)
        self.r2.start(arr_rgb["r2"]*100/255)
        self.g2.start(arr_rgb["g2"]*100/255)
        self.b2.start(arr_rgb["b2"]*100/255)
        
        
        
        
    def ledon(self):
        # GPIO.output(5, GPIO.HIGH)
        # GPIO.output(6, GPIO.HIGH)
        # GPIO.output(13, GPIO.HIGH)
        self.r1.ChangeDutyCycle(100)
        self.g1.ChangeDutyCycle(100)
        self.b1.ChangeDutyCycle(100)
    def ledoff(self):
        # GPIO.output(5, GPIO.LOW)
        # GPIO.output(6, GPIO.LOW)
        # GPIO.output(13, GPIO.LOW)
        self.r1.ChangeDutyCycle(0)
        self.g1.ChangeDutyCycle(0)
        self.b1.ChangeDutyCycle(0)
        
    def change_ledcolor1(self, arg):
        self.r1.ChangeDutyCycle(arg['r']*100/255)
        self.g1.ChangeDutyCycle(arg['g']*100/255)
        self.b1.ChangeDutyCycle(arg['b']*100/255)
        
    def change_ledcolor2(self, arg):
        self.r2.ChangeDutyCycle(arg['r']*100/255)
        self.g2.ChangeDutyCycle(arg['g']*100/255)
        self.b2.ChangeDutyCycle(arg['b']*100/255)
        
    def store_ledcolor1(self,arg):
        store_rgb(1,1,arg)
        
    def store_ledcolor2(self,arg):
        store_rgb(1,2,arg)
        
    def cameraPicture(self,arg):
        filename = 'DCIM/temp'+str(arg)+'.jpg'
        print filename
        #self.camera.resolution = (800, 600)
        self.camera.resolution = (1024, 768)
        self.camera.capture(filename)
        sendToClients({"action": "result_camerapicture", "value": 1, "filename": filename,"arg": arg})
        
        """
        print time.time()
        arr = '{"action": "html", "option": "display", "item": "testimage", "value": "none"}'
        for client in clients:
            client.sendMessage(u''+arr)
        arr = '{"action": "html", "option": "src", "item": "testimage", "value": "temp.jpg#'+str(int(time.time()))+'"}'
        for client in clients:
            client.sendMessage(u''+arr)
        arr = '{"action": "html", "option": "display", "item": "testimage", "value": "block"}'
        for client in clients:
            client.sendMessage(u''+arr)
        """
        
    def compare_code(self,arg):
        self.pw = get_password(1)
        print str(self.pw)
        print str(arg['pin'])
        if str(self.pw) == str(arg['pin']):
            print "passt"
            sendToClients({"action": "result_compare_code", "value": 1})
        else:
            print "falsch"
            sendToClients({"action": "result_compare_code", "value": 0})

    def change_code(self,arg):
        newpin = arg['pin']
        if change_password(1,newpin):
            print "PW erfolgreich geaendert"
            sendToClients({"action": "result_change_password", "value": 1})
        else:
            print "Fehler beim Passwort aendern"
            sendToClients({"action": "result_change_password", "value": 0})
    
