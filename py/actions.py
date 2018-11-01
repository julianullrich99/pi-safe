import RPi.GPIO as GPIO
# from picamera import PiCamera
import picamera
# import base64
# import subprocess
from subprocess import call
from common import *
import logging
import time
import json
import os
import sys
import sqlite3
from datetime import datetime
from mail import sendmymail
import __main__

# from __main__ import clients

GPIO.setmode(GPIO.BCM)
camera = picamera.PiCamera()
  

# wenn Pin 21 gewackelt hat, soll ein Alarm ausgeloest werden!
def set_alarm(channel):
   print "Alarm!!"
   state.state = state.stateName.index('alarm')


GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(21, GPIO.FALLING, callback=set_alarm, bouncetime=300)

def sendToClients(arr):
    for client in clients:
        client.sendMessage(u"" + json.dumps(arr))

def dbconnect():
    global dbfile
    if not os.path.exists(dbfile):
        logging.warning("DB misafe.db doesn't exists - DB will be created.")
        create_db()

def create_db():
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    # Tabelle user erzeugen
    sql = 'CREATE TABLE user(id INTEGER, pin1 INTEGER, pin2 INTEGER)'
    cursor.execute(sql)
    sql = "INSERT INTO user VALUES(" + str(1) + \
        ", " + str(1234) + ", " + str(1234) + ")"
    cursor.execute(sql)
    con.commit()

    # Tabelle colors erzeugen
    sql = 'CREATE TABLE colors(id INTEGER, id_user INTEGER, r1 INTEGER, g1 INTEGER, b1 INTEGER, r2 INTEGER, g2 INTEGER, b2 INTEGER)'
    cursor.execute(sql)
    sql = "INSERT INTO colors (id,id_user,r1,g1,b1,r2,g2,b2)VALUES(1,1,255,0,255,255,255,0)"
    cursor.execute(sql)
    con.commit()


    # Tabelle colors erzeugen
    sql = 'CREATE TABLE pictures(id INTEGER, filename STRING, user INTEGER)'
    cursor.execute(sql)
    con.commit()
    con.close()
    logging.debug("Database " + dbfile + "created with content %s", sql)

def get_password(user):
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "SELECT * FROM user WHERE id = " + str(user)
    cursor.execute(sql)
    for data in cursor:
        pw1 = data[1]
        pw2 = data[2]

    con.close()
    return (pw1)

def change_password(user, newpin):
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "UPDATE user SET pin1 = " + str(newpin) + " WHERE id = " + str(user)
    cursor.execute(sql)
    con.commit()
    con.close()
    return (1)

def store_rgb(user, which, rgb):
    global dbfile
    w = str(which)
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "UPDATE colors SET "
    sql += "r" + w + " = " + str(rgb['r']) + ", "
    sql += "g" + w + " = " + str(rgb['g']) + ", "
    sql += "b" + w + " = " + str(rgb['b']) + " "
    sql += "WHERE id = 1"
    logging.debug(sql)
    cursor.execute(sql)
    con.commit()
    con.close()
    globalrgb['r'+w] = rgb['r']
    globalrgb['g'+w] = rgb['g']
    globalrgb['b'+w] = rgb['b']
    return (1)

def get_rgb():
    global globalrgb
    if globalrgb == {}:
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
        arr = {"r1": r1, "g1": g1, "b1": b1, "r2": r2, "g2": g2, "b2": b2}
        con.close()
        globalrgb = arr
        return (arr)
    else:
        return globalrgb

def store_picture(user, filename, ts):
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "INSERT INTO pictures (filename, ts, user)  VALUES ('" + filename + "', " + ts + ", " + str(user) + ")"
    logging.debug(sql)
    try:
        cursor.execute(sql)
        con.commit()
        con.close()
    except:
        logging.debug("Unexpected error: %s", sys.exc_info())
        raise

    return (1)

def triggerLED(functionName, *args):
    global colors
    while colors.colorTrigger.isSet():
        pass
    colors.colorEvent = functionName
    colors.colorEventArgs = args
    colors.colorTrigger.set()
    logging.debug("triggered: %s", colors.colorEvent)

def get_pictures(count):
    global dbfile
    limit = count
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()

    # Anzahl ermitteln
    sql = "SELECT count(*) FROM pictures"
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        countall = result[0]
        logging.debug("Count of Pictures: "+str(countall))
    except:
        logging.debug("Unexpected error: %s", sys.exc_info())
        raise

    sql = "SELECT  * FROM pictures LIMIT "+str(limit)+" OFFSET " + str(countall - limit)
    logging.debug(sql)
    try:
        cursor.execute(sql)
        files = []
        for data in cursor:
            filename = data[1]
            mydate = datetime.utcfromtimestamp(int(data[2])).strftime('%Y-%m-%d %H:%M:%S')
            user=data[3]
            #files.append({"filename":data[1],"date":data[2],"user":data[3]})
            files.append({"filename":filename,"date":mydate,"user":user})
        #arr = {"files": files, "offset": offset}
        arr = {"files": files}
        con.close()
        return (arr)
    except:
        logging.debug("Unexpected error: %s", sys.exc_info())
        raise

def do_del_picture(file):
    global dbfile
    con = sqlite3.connect(dbfile)
    cursor = con.cursor()
    sql = "DELETE FROM pictures WHERE filename = '" + str(file) + "'"
    logging.debug(sql)
    try:
        cursor.execute(sql)
        con.commit()
        con.close()
    except:
        logging.debug("Unexpected error: %s", sys.exc_info())
        raise
    return (1)


def takeCameraPicture(arg):
    global camera
    logging.debug("test: %s ", 'start cameraPicture')

    ts = str(int(time.time()))
    path = '/var/www/html/DCIM/'
    filename = 'pisnap_' + ts + '.jpg'
    filename_response = '/DCIM/' + filename
    logging.debug("Filename: %s ", path + filename)
    camera.resolution = (1024, 768)
    #camera.resolution = (800, 600)
    triggerLED("ledon")
    try:
      camera.capture(path + filename)
      #sendToClients({"action": "result_camerapicture","value": 1, "filename": filename_response, "arg": arg})
      store_picture(1, filename, ts)
      triggerLED("ledoff")
      return (1)
    except Exception as e:
      #sendToClients({"action": "error", "type": "cameraPicture"})
      logging.debug("Error in taking picture: %s", e)
      triggerLED("ledoff")
      raise
      return (2)

def shutdown(arg):
    #call("sudo nohup shutdown -h now", shell=True)
    #ser.close()
    logging.debug("Remote Shutdown: %s ", arg['type'])
    if arg['type'] == 1:
      call("sudo shutdown -h now", shell=True)
    #  os.system("sudo shutdown -h now")
      # oder
      # subprocess.call(['shutdown', '-h', 'now'], shell=False)
    if arg['type'] == 2:
      call("sudo shutdown -r now", shell=True)
    #  os.system("sudo shutdown -r now")
    #sys.exit()

def testmove_motor(arg):
    logging.debug("Testmove Motor: %s ", arg['motor'])
    logging.debug("duty1: %s ", arg['duty1'])
    logging.debug("duty2: %s ", arg['duty2'])
    GPIO.setmode(GPIO.BCM)
    if arg['motor'] == 'lock':
        l1 = GPIO.PWM(mapping.lock.out1, 200)
        l2 = GPIO.PWM(mapping.lock.out2, 200)
        l1.start(int(arg['duty1']))
        l2.start(int(arg['duty2']))
        return(1)
    if arg['motor'] == 'door':
        d1 = GPIO.PWM(mapping.door.out1, 200)
        d2 = GPIO.PWM(mapping.door.out2, 200)
        d1.start(int(arg['duty1']))
        d2.start(int(arg['duty2']))
        return(2)




class actions:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        logging.debug("Connecting to Database")
        dbconnect()
        logging.debug("Database Connected")
        #self.camera = PiCamera()

    def get_state(self):
        sendToClients({"action": "state", "value": str(state.state)})
        logging.debug("sending state: %s", state.state)

    def store_ledcolor1(self, arg):
        triggerLED("store_ledcolor1", arg)
        print colors.colorEvent

    def store_ledcolor2(self, arg):
        triggerLED("store_ledcolor2", arg)

    def get_ledcolor(self, arg):
        triggerLED("get_ledcolor", arg)

    def cameraPicture(self, arg):
        gallery_count = arg['count']
        #gallery_offset = arg['offset']
        takeCameraPicture(arg)
        arr = get_pictures(gallery_count)
        sendToClients({"action": "result_get_gallery","list": arr, "arg": arg})
        #sendToClients({"action": "result_camerapicture","value": 1, "filename": filename_response, "arg": arg})

    def compare_code(self, arg):
        self.pw = get_password(1)
        logging.debug("stored pin: %s", str(self.pw))
        logging.debug("received pin: %s", str(arg['pin']))

        if str(self.pw) == str(arg['pin']):
            logging.debug("PIN corect")
            sendToClients({"action": "result_compare_code", "value": 1})
            #unlocked.set()
            opened.set()
        else:
            logging.debug("PIN wrong")
            sendToClients({"action": "result_compare_code", "value": 0})
            # triggerLED("blinkHelp", {"count": colors.blinkCount, "color": colors.blinkWrong, "which": colors.blinkWhich, "speed": colors.blinkSpeed})
            triggerLED("blink", colors.blinkCount, colors.blinkWrong, colors.blinkWhich, colors.blinkSpeed)
            # sendmymail("Pi-Safe Password Attempt wrong: "+str(arg['pin']))

    def change_code(self, arg):
        newpin = arg['pin']
        if change_password(1, newpin):
            logging.debug("PIN change successful")
            sendToClients({"action": "result_change_password", "value": 1})
        else:
            logging.debug("PIN change successful")
            sendToClients({"action": "result_change_password", "value": 0})

    def lock(self):
        #unlocked.clear()
        opened.clear()

    def pinView(self, arg):
        option = arg['view']

    def get_gallery(self, arg):
        gallery_count = arg['count']
        arr = get_pictures(gallery_count)
        sendToClients({"action": "result_get_gallery","list": arr, "arg": arg})

    def del_picture(self, arg):
        rtn = do_del_picture(arg['file'])
        gallery_count = arg['count']
        if(rtn == 1):
          arr = get_pictures(gallery_count)
          sendToClients({"action": "result_get_gallery","list": arr, "arg": arg})

    def move_motor(self, arg):
        rtn = testmove_motor(arg)
        sendToClients({"action": "result_move_motor","arg": arg})

    def systemshutdown(self, arg):
        shutdown(arg)
        
    def testfunction(self, arg):
        state.state = 10
        sendToClients({"action": "state", "value": str(state.state)})


