from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import RPi.GPIO as GPIO
import json
from actions import actions
from se import *
from common import *

GPIO.setmode(GPIO.BCM)

action = actions()
motorcontrol = motorcontrol()

GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  

def my_callback(channel):
  print "falling edge detected"
  for client in clients:
    client.sendMessage(u""+json.dumps({"action": "text", "item": "div1", "value": "aus"}))
  GPIO.remove_event_detect(19)
  GPIO.add_event_detect(19, GPIO.RISING, callback=my_callback2, bouncetime=300)

def my_callback2(channel):
  print "rising edge detected"
  for client in clients:
    client.sendMessage(u'{"action": "text", "item": "div1", "value": "an"}')
  GPIO.remove_event_detect(19)
  GPIO.add_event_detect(19, GPIO.FALLING, callback=my_callback, bouncetime=300)

GPIO.add_event_detect(19, GPIO.FALLING, callback=my_callback, bouncetime=300)
#GPIO.add_event_detect(19, GPIO.RISING, callback=my_callback2, bouncetime=300)


# clients = [];

def handle(msg):
  print "message income"
  #print msg
  event = json.loads(msg)
  print event["action"]
  # echo = ""
  if hasattr(action, event["action"]):
    try:
      print event["arg"]
      getattr(action, event["action"])(event["arg"])
      # echo = function
    except:
      print "no args"
      getattr(action, event["action"])()

class protocol(WebSocket):
  def handleMessage(self):
    # echo message back to client
    print self.data;
    handle(self.data)
    for client in clients:
      client.sendMessage(self.data)

  def handleConnected(self):
    print(self.address, 'connected')
    #for client in clients:
    #  client.sendMessage(u"connected")
    clients.append(self)

  def handleClose(self):
    print(self.address, 'closed')
    clients.remove(self)

#getattr(action, "testfun")()
server = SimpleWebSocketServer('', 8000, protocol)
print "WebSocket Server started at localhost:8000"
server.serveforever()
