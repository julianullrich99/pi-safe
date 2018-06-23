import RPi.GPIO as GPIO



try:
  import server
except KeyboardInterrupt:
  # print dir()
  print "Exiting by user interrupt..."
except Exception as exception:
  print "Exiting by error..."
  print(exception.message)
finally:
  # server.sendClose()
  print "Cleaning up GPIO settings..."
  GPIO.cleanup()
  print "Fininshed."
