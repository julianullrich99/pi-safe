import RPi.GPIO as GPIO
import threading
import time
from common import *

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
        i += 0.001 if i < 20 else 0
        d1.ChangeDutyCycle(i)
        time.sleep(0.05)
    d1.ChangeDutyCycle(0)
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
    l2.ChangeDutyCycle(0)
    print "lock closed"
    print "motors initialized"
    state.state = 0

def StateEngine():
    while 1:
        print "state check"
