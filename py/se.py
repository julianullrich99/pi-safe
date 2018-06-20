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
def initSe(PinMap, state):
    GPIO.setup(PinMap.door.out1, GPIO.OUT)
    GPIO.setup(PinMap.door.out2, GPIO.OUT)
    GPIO.setup(PinMap.door.in1, GPIO.IN)
    GPIO.setup(PinMap.lock.out1, GPIO.OUT)
    GPIO.setup(PinMap.lock.out2, GPIO.OUT)
    GPIO.setup(PinMap.lock.in1, GPIO.IN)
    GPIO.setup(PinMap.lock.in2, GPIO.IN)
    if state.state == state.stateName.index("init"):


def StateEngine(state):
    while 1:
