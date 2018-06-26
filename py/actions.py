import RPi.GPIO as GPIO
from picamera import PiCamera
# import base64
from common import *
import logging
import time
import json
import os
import sys
import sqlite3
import __main__

# from __main__ import clients

GPIO.setmode(GPIO.BCM)

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
    sql = "INSERT INTO pictures (filename, ts, user)  VALUES ('" + \
        filename + "', " + ts + ", " + str(user) + ")"
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

class actions:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        logging.debug("Connecting to Database")
        dbconnect()
        logging.debug("Database Connected")
        self.camera = PiCamera()

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
        ts = str(int(time.time()))
        path = '/var/www/html/DCIM/'
        filename = 'pisnap_' + ts + '.jpg'
        filename_response = '/DCIM/' + filename
        logging.debug("Filename: %s ", filename)
        # self.camera.resolution = (800, 600)
        triggerLED("ledon")
        try:
            self.camera.resolution = (1024, 768)
            self.camera.capture(path + filename)
            sendToClients({"action": "result_camerapicture",
                           "value": 1, "filename": filename_response, "arg": arg})
            store_picture(1, filename, ts)
            triggerLED("ledoff")
        except Exception as e:
            sendToClients({"action": "error", "type": "cameraPicture"})
            logging.debug("Error in taking picture: %s", e)
            triggerLED("ledoff")

    def compare_code(self, arg):
        self.pw = get_password(1)
        logging.debug("stored pin: %s", str(self.pw))
        logging.debug("received pin: %s", str(arg['pin']))
        if str(self.pw) == str(arg['pin']):
            logging.debug("PIN corect")
            sendToClients({"action": "result_compare_code", "value": 1})
            unlocked.set()
        else:
            logging.debug("PIN wrong")
            sendToClients({"action": "result_compare_code", "value": 0})
            # triggerLED("blinkHelp", {"count": colors.blinkCount, "color": colors.blinkWrong, "which": colors.blinkWhich, "speed": colors.blinkSpeed})
            triggerLED("blink", colors.blinkCount, colors.blinkWrong, colors.blinkWhich, colors.blinkSpeed)

    def change_code(self, arg):
        newpin = arg['pin']
        if change_password(1, newpin):
            logging.debug("PIN change successful")
            sendToClients({"action": "result_change_password", "value": 1})
        else:
            logging.debug("PIN change successful")
            sendToClients({"action": "result_change_password", "value": 0})

    def lock(self):
        unlocked.clear()

    def pinView(self, arg):
		option = arg['view']
