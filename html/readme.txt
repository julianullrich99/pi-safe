dependencies:

python server:
  SimpleWebSocketServer (https://github.com/dpallot/simple-websocket-server)
  Install: sudo pip install git+https://github.com/dpallot/simple-websocket-server.git

  RPi.GPIO
  json
js:
  iro.min.js
  jquery-knob
  jquery
  


Aufruf der Seite als Vollbild:
DISPLAY=:0 chromium-browser --kiosk http://raspi01
