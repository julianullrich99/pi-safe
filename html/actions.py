import RPi.GPIO as GPIO
from picamera import PiCamera
# import base64
from common import *

import time
import json
import os, sys, sqlite3

dbfile  = "/var/www/db/misafe.db"
state = 0

# from __main__ import clients

GPIO.setmode(GPIO.BCM)

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
'''
def morph_rgb(rgb,which):
    GPIO.setmode(GPIO.BCM)
    arr_rgb = get_rgb()
    arr_rgb_end = rgb
    n = 100
    which = 1
    r1 = arr_rgb["r"+str(which)] # Anfangswerte
    g1 = arr_rgb["g"+str(which)]
    b1 = arr_rgb["b"+str(which)]
    print("RGB:"+arr_rgb_end["r"])
    dr1 = arr_rgb_end["r"] - r1 #Differenz Ende - Anfang
    dg1 = arr_rgb_end["g"] - g1
    db1 = arr_rgb_end["b"] - b1
    
    GPIO.setup(5, GPIO.OUT) #R1
    GPIO.setup(6, GPIO.OUT) #G1
    GPIO.setup(13, GPIO.OUT)#B1
    
    out_r1 = GPIO.PWM(5, 100) #Pin, Frequency
    out_g1 = GPIO.PWM(6, 100)
    out_b1 = GPIO.PWM(13, 100)
    
    out_r1.start(arr_rgb["r"+str(which)]*100/255)
    out_g1.start(arr_rgb["g"+str(which)]*100/255)
    out_b1.start(arr_rgb["b"+str(which)]*100/255)
    
    
    for counter in range(0,n+1):
      
      
      r1_end = r1 + (counter * dr1 /100) 
      g1_end = g1 + (counter * dg1 /100)
      b1_end = b1 + (counter * db1 /100)

      out_r1.ChangeDutyCycle(r1_end*100/255)
      out_g1.ChangeDutyCycle(g1_end*100/255)
      out_b1.ChangeDutyCycle(b1_end*100/255)
      
      print("R"+str(r1_end)+" G"+str(g1_end)+" B"+str(b1_end))
      time.sleep(0.01)
'''

def open_rw():
    GPIO.setup(22, GPIO.OUT) 
    GPIO.setup(23, GPIO.OUT) 
    GPIO.output(22, GPIO.HIGH)
    GPIO.output(23, GPIO.LOW)
    
def close_rw():
    GPIO.setup(22, GPIO.OUT) 
    GPIO.setup(23, GPIO.OUT) 
    GPIO.output(22, GPIO.LOW)
    GPIO.output(23, GPIO.HIGH)
    
    
class actions:
    def __init__(self):
      dbconnect()
      self.camera = PiCamera()
      
      self.correctur_r = 1
      self.correctur_g = 0.6
      self.correctur_b = 0.4
      
      arr_rgb = get_rgb()
      print("Color initialisation:")
      print("RGB1: " + str(arr_rgb["r1"])+ " " + str(arr_rgb["g1"])+ " " + str(arr_rgb["b1"]))
      print("RGB2: " + str(arr_rgb["r2"])+ " " + str(arr_rgb["g2"])+ " " + str(arr_rgb["b2"]))

      
      #GPIO.setWarnings(false)
      GPIO.setup(5, GPIO.OUT) #R1
      GPIO.setup(6, GPIO.OUT) #G1
      GPIO.setup(13, GPIO.OUT)#B1
      
      self.r1 = GPIO.PWM(5, 200) #Pin, Frequency
      self.g1 = GPIO.PWM(6, 200)
      self.b1 = GPIO.PWM(13, 200)

      self.r1.start(self.correctur_r * (arr_rgb["r1"]*100/255))
      self.g1.start(self.correctur_g * (arr_rgb["g1"]*100/255))
      self.b1.start(self.correctur_b * (arr_rgb["b1"]*100/255))
      
      GPIO.setup(17, GPIO.OUT)#R2
      GPIO.setup(18, GPIO.OUT)#G2
      GPIO.setup(27, GPIO.OUT)#B2
      self.r2 = GPIO.PWM(17, 200)
      self.g2 = GPIO.PWM(18, 200)
      self.b2 = GPIO.PWM(27, 200)
      self.r2.start(self.correctur_r * (arr_rgb["r2"]*100/255))
      self.g2.start(self.correctur_r * (arr_rgb["g2"]*100/255))
      self.b2.start(self.correctur_r * (arr_rgb["b2"]*100/255))
      
      
          

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
        
    def testopen(self, arg):
        #open_rw() 
        print("rw oeffnen")
        
    def testclose(self, arg):
        #close_rw()
        print("rw schliessen")
        
    def morphto(self, rgb ,which):
        print("morphing : " + str(which))
        arr_rgb = get_rgb()
        arr_rgb_end = rgb
        n = 100
        
        
        r1 = arr_rgb["r"+str(which)] # Anfangswerte
        g1 = arr_rgb["g"+str(which)]
        b1 = arr_rgb["b"+str(which)]
        
        dr1 = arr_rgb_end["r"] - r1 #Differenz Ende - Anfang
        dg1 = arr_rgb_end["g"] - g1
        db1 = arr_rgb_end["b"] - b1
        
        
        
        for counter in range(0,n+1):
          r1_end = r1 + (counter * dr1 /100) 
          g1_end = g1 + (counter * dg1 /100)
          b1_end = b1 + (counter * db1 /100)
          
          # print("R"+str(r1_end)+" G"+str(g1_end)+" B"+str(b1_end))
          
          if which == 1:
            self.r1.ChangeDutyCycle(self.correctur_r * (r1_end*100/255))
            self.g1.ChangeDutyCycle(self.correctur_g * (g1_end*100/255))
            self.b1.ChangeDutyCycle(self.correctur_b * (b1_end*100/255))
          
          if which == 2:
            self.r2.ChangeDutyCycle(self.correctur_r * (r1_end*100/255))
            self.g2.ChangeDutyCycle(self.correctur_g * (g1_end*100/255))
            self.b2.ChangeDutyCycle(self.correctur_b * (b1_end*100/255))

          time.sleep(0.01)

    def store_ledcolor1(self,arg):
        self.morphto(arg,1)
        store_rgb(1,1,arg)
        

    def store_ledcolor2(self,arg):
        self.morphto(arg,2)
        store_rgb(1,2,arg)
        
        
    def cameraPicture(self,arg):
        filename = 'DCIM/temp'+str(arg)+'.jpg'
        print filename 
        #self.camera.resolution = (800, 600)
        self.camera.resolution = (1024, 768)
        self.camera.capture( filename )
        sendToClients({"action": "result_camerapicture", "value": 1, "filename": filename,"arg": arg})
              
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
    
