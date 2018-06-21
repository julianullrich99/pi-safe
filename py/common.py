# from __main__ import threading
import threading

clients = []

unlock = threading.Event()

openDuration = 10.0
rampDuration = 2.0
vmax = 100
vclose = 70

class Object(object):
    pass

class mapping:
    door = Object()
    lock = Object()
    door.out1 = 10 #zu
    door.out2 = 9 #auf
    door.in1 = 11 #zu
    lock.out1 = 22 #auf
    lock.out2 = 23 #zu
    lock.in1 = 24 #auf
    lock.in2 = 25 #zu

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
