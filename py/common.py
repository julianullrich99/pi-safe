# from __main__ import threading
import threading

clients = []

unlock = threading.Event()

<<<<<<< HEAD
openDuration = 4.0
rampDuration = 2.0
=======
openDuration = 1.0
rampDuration = 0.5
>>>>>>> 120dae27c85ce81f37d2b459a86f94d17ad05e33
vmax = 100
vclose = 70

class Object(object):
    pass

class mapping:
    door = Object()
    lock = Object()
    ledBody = Object()
    ledEdge = Object()
    door.out1 = 10 #zu
    door.out2 = 9 #auf
    door.in1 = 11 #zu
    lock.out1 = 22 #auf
    lock.out2 = 23 #zu
    lock.in1 = 24 #auf
    lock.in2 = 25 #zu
    ledBody.r = 17
    ledBody.g = 18
    ledBody.b = 27
    ledEdge.r = 5
    ledEdge.g = 6
    ledEdge.b = 13

class state:
    state = 5
    stateName = ['locked',
                'rw_opening',
                'rw_closing',
                'rw_unlocked',
                'safe_door_opening',
                'safe_door_closing',
                'unlocked',
                'init']
