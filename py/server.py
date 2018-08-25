from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import threading
import logging
import RPi.GPIO as GPIO
import json
from actions import actions
# from se import *
from common import *
import se

FORMAT = "[%(lineno)4s:%(filename)-10s - %(funcName)10s()] %(message)s"
# FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
action = actions()


logging.debug('Init StateEngine')
se.initSe() # init StateEngine

StateMachine = threading.Thread(name='stateMachine', target=se.StateEngine, args=(opened,))
#StateMachine = threading.Thread(name='stateMachine', target=se.StateEngine, args=(unlocked,))
StateMachine.setDaemon(True)

StateMachine.start()

ColorMachine = se.ColorEngine(colors.colorTrigger)
ColorMachine.setDaemon(True)

ColorMachine.start()

# motorcontrol = motorcontrol()

GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#
#
def my_callback(channel):
   print "falling edge detected"
#   for client in clients:
#     client.sendMessage(u""+json.dumps({"action": "text", "item": "div1", "value": "aus"}))
#   GPIO.remove_event_detect(19)
#   GPIO.add_event_detect(19, GPIO.RISING, callback=my_callback2, bouncetime=300)
#
# def my_callback2(channel):
#   print "rising edge detected"
#   for client in clients:
#     client.sendMessage(u'{"action": "text", "item": "div1", "value": "an"}')
#   GPIO.remove_event_detect(19)
#   GPIO.add_event_detect(19, GPIO.FALLING, callback=my_callback, bouncetime=300)
#
GPIO.add_event_detect(19, GPIO.FALLING, callback=my_callback, bouncetime=300)
# GPIO.add_event_detect(19, GPIO.RISING, callback=my_callback, bouncetime=300)


# clients = [];


def handle(msg):
  logging.debug("message income")
  # print msg
  event = json.loads(msg)
  logging.debug("action: %s",event["action"])
  # echo = ""
  if hasattr(action, event["action"]):
    try:
      logging.debug("arguments: %s",event["arg"])
      getattr(action, event["action"])(event["arg"])
      # echo = function
    except:
      logging.debug("arguments: none")
      getattr(action, event["action"])()

class protocol(WebSocket):
  def handleMessage(self):
    # echo message back to client
    # print self.data;

    for client in clients:
      client.sendMessage(self.data)
    handle(self.data)

  def handleConnected(self):
    logging.debug('%s connected', self.address)
    #for client in clients:
    #  client.sendMessage(u"connected")
    clients.append(self)

  def handleClose(self):
    logging.debug('%s closed', self.address)
    clients.remove(self)


logging.debug("Starting WebSocket Server on localhost:8000")
server = SimpleWebSocketServer('', 8000, protocol)
logging.debug("WebSocket Server started at localhost:8000")
server.serveforever()




