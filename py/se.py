import RPi.GPIO as GPIO
import threading
import time
from common import *
from actions import sendToClients

GPIO.setmode(GPIO.BCM)

class motorcontrol:
 	def __init__(self):
	    print "Initializing Motors"
	    # GPIO.setup(22, GPIO.OUT) #DIR1
	    # GPIO.setup(23, GPIO.OUT) #DIR2
	    # GPIO.output(22, GPIO.HIGH)
	    # GPIO.output(23, GPIO.HIGH)
 	def rw_open(self):
	    print "rw_open"
	    GPIO.output(22, GPIO.LOW)
	    GPIO.output(23, GPIO.HIGH)
	def rw_close(self):
	    print "rw_close"
	    GPIO.output(22, GPIO.HIGH)
	    GPIO.output(23, GPIO.LOW)
	def rw_open(self):
	    print "rw_open"
	    GPIO.output(22, GPIO.LOW)
	    GPIO.output(23, GPIO.HIGH)
	def rw_init(self):
		print "init"

#class StateEngine(threading.Thread):
def initSe():
    GPIO.setup(mapping.door.out1, GPIO.OUT)
    GPIO.setup(mapping.door.out2, GPIO.OUT)
    GPIO.setup(mapping.door.in1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mapping.lock.out1, GPIO.OUT)
    GPIO.setup(mapping.lock.out2, GPIO.OUT)
    GPIO.setup(mapping.lock.in1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mapping.lock.in2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if state.state == state.stateName.index("init"):
		print "init StateEngine"
    print "closing door"
    d1 = GPIO.PWM(mapping.door.out1, 200)
    d2 = GPIO.PWM(mapping.door.out2, 200)
    i = 0
    d1.start(i)
    d2.start(0)
    while GPIO.input(mapping.door.in1):
        i += 1 if i < vclose else 0
        d1.ChangeDutyCycle(i)
        time.sleep(float(rampDuration)/vclose)
    d1.stop()
    d2.stop()
    print "door closed"
    print "closing lock"
    l1 = GPIO.PWM(mapping.lock.out1, 200)
    l2 = GPIO.PWM(mapping.lock.out2, 200)
    i = 0
    l1.start(0)
    l2.start(i)
    while GPIO.input(mapping.lock.in2):
        i += 1 if i < 50 else 0
        l2.ChangeDutyCycle(i)
        time.sleep(0.01)
    l1.stop()
    l2.stop()
    print "lock closed"
    print "motors initialized"
    state.state = state.stateName.index('locked')

def StateEngine(e):
    while 1:
      if e.isSet():
        while 1:
          if e.isSet():
            state.state = state.stateName.index('rw_opening')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            GPIO.setmode(GPIO.BCM)
            print "opening lock"
            l1 = GPIO.PWM(mapping.lock.out1, 200)
            l2 = GPIO.PWM(mapping.lock.out2, 200)
            i = 0
            l1.start(i)
            l2.start(0)
            # print "PWMs initialized"
            while GPIO.input(mapping.lock.in1):
              # print "moving lock", i
              i += 1 if i < 100 else 0
              l1.ChangeDutyCycle(i)
              time.sleep(0.01)
            l1.stop()
            l2.stop()
            print "lock open"
            state.state = state.stateName.index('rw_unlocked')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            if openDuration < 2 * rampDuration:
              print "cant open door, please set openDuration > 2 * rampDuration"
              e.clear()
              break
            print "opening door"
            state.state = state.stateName.index('safe_door_opening')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            d1 = GPIO.PWM(mapping.door.out1, 200)
            d2 = GPIO.PWM(mapping.door.out2, 200)
            i = 0
            d1.start(0)
            d2.start(i)
            if vmax > 100:
              print "cant open door, please set vmax <= 100"
              break
            while i < vmax:
              i += 1
              d2.ChangeDutyCycle(i)
              time.sleep(float(rampDuration)/vmax)
            before = time.time()
            while before + (openDuration - 2 * rampDuration) > time.time():
              time.sleep(0.1)
            while i > 0:
              i -= 1
              d2.ChangeDutyCycle(i)
              time.sleep(float(rampDuration)/vmax)
            d1.stop()
            d2.stop()
            print "unlocked"
            state.state = state.stateName.index('unlocked')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            while e.isSet():
              time.sleep(0.1)
          else:
            state.state = state.stateName.index('rw_unlocked')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            GPIO.setmode(GPIO.BCM)
            if openDuration < 2 * rampDuration:
              print "cant close door, please set openDuration > 2 * rampDuration"
              e.set()
              break
            print "closing door"
            state.state = state.stateName.index('safe_door_closing')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            d1 = GPIO.PWM(mapping.door.out1, 200)
            d2 = GPIO.PWM(mapping.door.out2, 200)
            i = 0
            d1.start(i)
            d2.start(0)
            if vmax > 100:
              print "cant close door, please set vmax <= 100"
              break
            while i < vmax and GPIO.input(mapping.door.in1):
              i += 1
              d1.ChangeDutyCycle(i)
              time.sleep(float(rampDuration)/vmax)
            before = time.time()
            while before + (openDuration - 2 * rampDuration - 1) > time.time() and GPIO.input(mapping.door.in1):
              time.sleep(0.1)
            while i > vclose and GPIO.input(mapping.door.in1):
              i -= 1
              d1.ChangeDutyCycle(i)
              time.sleep(float(rampDuration)/vmax)
            while GPIO.input(mapping.door.in1):
              time.sleep(0.1)
            d1.stop()
            d2.stop()
            print "door closed"
            state.state = state.stateName.index('rw_unlocked')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            print "closing lock"
            l1 = GPIO.PWM(mapping.lock.out1, 200)
            l2 = GPIO.PWM(mapping.lock.out2, 200)
            i = 0
            l1.start(0)
            l2.start(i)
            # print "PWMs initialized"
            while GPIO.input(mapping.lock.in2):
              # print "moving lock", i
              i += 1 if i < 70 else 0
              l2.ChangeDutyCycle(i)
              time.sleep(0.01)
            l1.stop()
            l2.stop()
            print "lock closed"
            state.state = state.stateName.index('locked')
            sendToClients({"action": "result_get_state", "value": str(state.state)})
            while not e.isSet():
              time.sleep(0.1)
