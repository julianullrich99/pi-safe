import RPi.GPIO as GPIO

class motorcontrol:
  def __init__(self):
    print "Initializing Motors"
    GPIO.setup(22, GPIO.OUT) #DIR1
    GPIO.setup(23, GPIO.OUT) #DIR2
    GPIO.output(22, GPIO.HIGH)
    GPIO.output(23, GPIO.HIGH)
  def rw_open(self):
    print "rw_open"
    GPIO.output(22, GPIO.LOW)
    GPIO.output(23, GPIO.HIGH)
  def rw_close(self):
    print "rw_close"
    GPIO.output(22, GPIO.HIGH)
    GPIO.output(23, GPIO.LOW)

def rw_open():
    print "rw_open"
    GPIO.output(22, GPIO.LOW)
    GPIO.output(23, GPIO.HIGH)    