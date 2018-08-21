import RPi.GPIO as GPIO
import threading
import time
from common import *
from actions import sendToClients, get_rgb, store_rgb, triggerLED
import logging
import __main__

GPIO.setmode(GPIO.BCM)

timeout = 0
timeout_time = 10

class Timer(threading.Thread):
    def __init__(self, func, sec=10):
        super(Timer, self).__init__()
        self.func = func
        self.sec = sec
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            t = time.time()
            
            time_elapsed = time.time()-t
            time.sleep(self.sec-time_elapsed if time_elapsed > 0 else 0)
            self.func()


def startTimeout():
    global timeout
    logging.debug('Timeout started')
    timeout = 0
    t.start() # after x seconds, function will called

def fireTimeout():
    global timeout
    logging.debug('Timeout expired')
    timeout = 1
    t.stop()
    
    
t = Timer(fireTimeout,timeout_time)

def get_ledcolor1(arg):
    arr_rgb = get_rgb()
    r = arr_rgb["r" + str(arg)]  # Anfangswerte
    g = arr_rgb["g" + str(arg)]
    b = arr_rgb["b" + str(arg)]
    rgb = {"r": r, "g": g, "b": b}
    #sendToClients({"action": "result_get_rgb","value": rgb, "arg": arg})
    return rgb


def initSe():
    GPIO.setup(mapping.door.out1, GPIO.OUT)
    GPIO.setup(mapping.door.out2, GPIO.OUT)
    GPIO.setup(mapping.door.in1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mapping.lock.out1, GPIO.OUT)
    GPIO.setup(mapping.lock.out2, GPIO.OUT)
    GPIO.setup(mapping.lock.in1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mapping.lock.in2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if state.state == state.stateName.index("init"):
        logging.debug("Initializing StateEngine")
    logging.debug("closing door")
    d1 = GPIO.PWM(mapping.door.out1, 200)
    d2 = GPIO.PWM(mapping.door.out2, 200)
    i = 0
    d1.start(i)
    d2.start(0)
    startTimeout()
    while GPIO.input(mapping.door.in1):
        if timeout == 1:
          state.state = state.stateName.index('timeout')
          d1.stop()
          d2.stop()
          return
        #logging.debug("timeout:%s",timeout)
        i += 1 if i < vclose else 0
        d1.ChangeDutyCycle(i)
        time.sleep(float(rampDuration) / vclose)
    d1.stop()
    d2.stop()
    logging.debug("door closed")
    logging.debug("closing lock")
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
    logging.debug("lock closed")
    logging.debug("motors initialized")
    state.state = state.stateName.index('locked')

def StateEngine(e):
    GPIO.setmode(GPIO.BCM)
    while 1:
        time.sleep(0.1)
        if e.isSet():
            while 1:
                time.sleep(0.05)
                if e.isSet():
                    triggerLED("ledon")
                    triggerLED("morphto", colors.colorOpen, colors.blinkWhich, lockDuration+openDuration)
                    state.state = state.stateName.index('rw_opening')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    logging.debug("opening lock")
                    l1 = GPIO.PWM(mapping.lock.out1, 200)
                    l2 = GPIO.PWM(mapping.lock.out2, 200)
                    i = 0
                    l1.start(i)
                    l2.start(0)
                    # print "PWMs initialized"
                    while GPIO.input(mapping.lock.in1):
                        # print "moving lock", i
                        i += 1 if i < 70 else 0
                        l1.ChangeDutyCycle(i)
                        time.sleep(0.01)
                    l1.stop()
                    l2.stop()
                    logging.debug("lock open")
                    state.state = state.stateName.index('rw_unlocked')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    if openDuration < 2 * rampDuration:
                        logging.warning(
                            "cant open door, please set openDuration > 2 * rampDuration")
                        e.clear()
                        break
                    logging.debug("opening door")
                    state.state = state.stateName.index('safe_door_opening')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    d1 = GPIO.PWM(mapping.door.out1, 200)
                    d2 = GPIO.PWM(mapping.door.out2, 200)
                    i = 0
                    d1.start(0)
                    d2.start(i)
                    if vmax > 100:
                        logging.warning(
                            "cant open door, please set vmax <= 100")
                        break
                    while i < vmax:
                        i += 1
                        d2.ChangeDutyCycle(i)
                        time.sleep(float(rampDuration) / vmax)
                    before = time.time()
                    while before + (openDuration - 2 * rampDuration) > time.time():
                        time.sleep(0.1)
                    while i > 0:
                        i -= 1
                        d2.ChangeDutyCycle(i)
                        time.sleep(float(rampDuration) / vmax)
                    d1.stop()
                    d2.stop()
                    logging.debug("open")
                    state.state = state.stateName.index('open')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    while e.isSet():
                        time.sleep(0.1)
                else:
                    #triggerLED("morphto", __main__.ColorMachine.get_ledcolor(colors.blinkWhich), colors.blinkWhich, lockDuration+openDuration, colors.colorOpen)
                    #triggerLED("morphto", __main__.ColorEngine.get_ledcolor(colors.blinkWhich), colors.blinkWhich, lockDuration+openDuration, colors.colorOpen)
                    
                    current_color = get_ledcolor1(colors.blinkWhich)
                    logging.debug("current_color"+str(current_color))
                    triggerLED("morphto", current_color, colors.blinkWhich, lockDuration+openDuration, colors.colorOpen)
                    
                    state.state = state.stateName.index('rw_unlocked')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    GPIO.setmode(GPIO.BCM)
                    if openDuration < 2 * rampDuration:
                        logging.warning(
                            "cant close door, please set openDuration > 2 * rampDuration")
                        e.set()
                        break
                    logging.debug("closing door")
                    state.state = state.stateName.index('safe_door_closing')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    d1 = GPIO.PWM(mapping.door.out1, 200)
                    d2 = GPIO.PWM(mapping.door.out2, 200)
                    i = 0
                    d1.start(i)
                    d2.start(0)
                    if vmax > 100:
                        logging.warning(
                            "cant close door, please set vmax <= 100")
                        break
                    while i < vmax and GPIO.input(mapping.door.in1):
                        i += 1
                        d1.ChangeDutyCycle(i)
                        time.sleep(float(rampDuration) / vmax)
                    before = time.time()
                    while before + (openDuration - 2 * rampDuration - 1) > time.time() and GPIO.input(mapping.door.in1):
                        time.sleep(0.1)
                    while i > vclose and GPIO.input(mapping.door.in1):
                        i -= 1
                        d1.ChangeDutyCycle(i)
                        time.sleep(float(rampDuration) / vmax)
                    while GPIO.input(mapping.door.in1):
                        time.sleep(0.1)
                    d1.stop()
                    d2.stop()
                    logging.debug("door closed")
                    state.state = state.stateName.index('rw_unlocked')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    logging.debug("closing lock")
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
                    logging.debug("lock closed")
                    state.state = state.stateName.index('locked')
                    sendToClients(
                        {"action": "state", "value": str(state.state)})
                    triggerLED("ledoff")
                    while not e.isSet():
                        time.sleep(0.1)
                        
                        

class ColorEngine(threading.Thread):
    def __init__(self, e):
        self.e = e
        threading.Thread.__init__(self)

        GPIO.setmode(GPIO.BCM)

        self.correctur_r = 1
        self.correctur_g = 0.6
        self.correctur_b = 0.4

        arr_rgb = get_rgb()
        logging.debug("Color initialisation:")
        logging.debug(
            "RGB1: " + str(arr_rgb["r1"]) + " " + str(arr_rgb["g1"]) + " " + str(arr_rgb["b1"]))
        logging.debug(
            "RGB2: " + str(arr_rgb["r2"]) + " " + str(arr_rgb["g2"]) + " " + str(arr_rgb["b2"]))

        # GPIO.setWarnings(false)
        # RGB Edges
        GPIO.setup(mapping.ledEdge.r, GPIO.OUT)  # R1
        GPIO.setup(mapping.ledEdge.g, GPIO.OUT)  # G1
        GPIO.setup(mapping.ledEdge.b, GPIO.OUT)  # B1

        self.r1 = GPIO.PWM(mapping.ledEdge.r, 200)  # Pin, Frequency
        self.g1 = GPIO.PWM(mapping.ledEdge.g, 200)
        self.b1 = GPIO.PWM(mapping.ledEdge.b, 200)

        self.r1.start(self.correctur_r * (arr_rgb["r1"] * 100 / 255))
        self.g1.start(self.correctur_g * (arr_rgb["g1"] * 100 / 255))
        self.b1.start(self.correctur_b * (arr_rgb["b1"] * 100 / 255))

        # RGB Body
        GPIO.setup(mapping.ledBody.r, GPIO.OUT)  # R2
        GPIO.setup(mapping.ledBody.g, GPIO.OUT)  # G2
        GPIO.setup(mapping.ledBody.b, GPIO.OUT)  # B2

        self.r2 = GPIO.PWM(mapping.ledBody.r, 200)
        self.g2 = GPIO.PWM(mapping.ledBody.g, 200)
        self.b2 = GPIO.PWM(mapping.ledBody.b, 200)

        self.r2.start(self.correctur_r * (arr_rgb["r2"] * 100 / 255))
        self.g2.start(self.correctur_r * (arr_rgb["g2"] * 100 / 255))
        self.b2.start(self.correctur_r * (arr_rgb["b2"] * 100 / 255))

        # LED White Inner Safe
        GPIO.setup(mapping.ledInner.w, GPIO.OUT)  # Pin 19, white LED
        self.w1 = GPIO.PWM(mapping.ledInner.w, 200)
        self.w1.start(0)  # off per default
        logging.debug("ColorMachine initialized")

    def run(self):
        # global colorEvent
        while 1:
            if (self.e.isSet()):
                self.e.clear()
                try:
                    getattr(self, colors.colorEvent)(*colors.colorEventArgs)
                except:
                    pass
            time.sleep(0.1)

    def ledon(self):
        # GPIO.output(5, GPIO.HIGH)
        self.w1.ChangeDutyCycle(100)

    def ledoff(self):
        # GPIO.output(5, GPIO.LOW)
        self.w1.ChangeDutyCycle(0)

    def morphto(self, rgb, which, speed=1.0, start=None):
        logging.debug(("morphing : " + str(which)))
        logging.debug("morphing time: %s", speed)
        if start is not None:                                 # konvertierung des start arrays
            try: start["r"+str(which)]
            except: start["r"+str(which)] = None
            if start["r"+str(which)] is None:
                start0 = {}
                for s in ["r","g","b"]:
                    start0[s+str(which)] = start[s]
                arr_rgb = start0
            else:
                arr_rgb = start
        else:
            arr_rgb = get_rgb()
        logging.debug(arr_rgb)
        arr_rgb_end = rgb
        n = 100


        r1 = arr_rgb["r" + str(which)]  # Anfangswerte
        g1 = arr_rgb["g" + str(which)]
        b1 = arr_rgb["b" + str(which)]

        dr1 = arr_rgb_end["r"] - r1  # Differenz Ende - Anfang
        dg1 = arr_rgb_end["g"] - g1
        db1 = arr_rgb_end["b"] - b1

        for counter in range(0, n + 1):
            r1_end = r1 + (counter * dr1 / 100)
            g1_end = g1 + (counter * dg1 / 100)
            b1_end = b1 + (counter * db1 / 100)

            # print("R"+str(r1_end)+" G"+str(g1_end)+" B"+str(b1_end))

            if which == 1:
                self.r1.ChangeDutyCycle(
                    self.correctur_r * (r1_end * 100 / 255))
                self.g1.ChangeDutyCycle(
                    self.correctur_g * (g1_end * 100 / 255))
                self.b1.ChangeDutyCycle(
                    self.correctur_b * (b1_end * 100 / 255))

            if which == 2:
                self.r2.ChangeDutyCycle(
                    self.correctur_r * (r1_end * 100 / 255))
                self.g2.ChangeDutyCycle(
                    self.correctur_g * (g1_end * 100 / 255))
                self.b2.ChangeDutyCycle(
                    self.correctur_b * (b1_end * 100 / 255))

            time.sleep(float(speed)/n)

    def store_ledcolor1(self, arg):
        self.morphto(arg, 1)
        store_rgb(1, 1, arg)

    def store_ledcolor2(self, arg):
        self.morphto(arg, 2)
        store_rgb(1, 2, arg)

    def get_ledcolor(self, arg):
        arr_rgb = get_rgb()
        r = arr_rgb["r" + str(arg)]  # Anfangswerte
        g = arr_rgb["g" + str(arg)]
        b = arr_rgb["b" + str(arg)]
        rgb = {"r": r, "g": g, "b": b}
        sendToClients({"action": "result_get_rgb",
                       "value": rgb, "arg": arg})
        return rgb

    def blinkHelp(self, args):
        self.blink(args["count"], args["color"], args["which"], args["speed"])

    def blink(self, count, rgb, which, speed):
        rgbStart = self.get_ledcolor(which)
        rgb0 = {"r": 0, "g": 0, "b": 0}
        rampDuration = float(speed) / (2 * count)
        self.morphto(rgb, which, rampDuration, rgbStart)
        if count > 1:
            for i in range(1, count):
                self.morphto(rgb0, which, rampDuration, rgb)
                self.morphto(rgb, which, rampDuration, rgb0)
        self.morphto(rgbStart, which, rampDuration, rgb)
