#Testscript zum Testen der GPIO am Pi
from server import *

def test():
  sendToClients({"action": "check_pincode", "value": "wird gecheckt"})
