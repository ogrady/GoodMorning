import pygame
import time
from pygame import locals
from threading import Thread

'''
Utility classes and exceptions.

version: 1.0
author: Daniel O'Grady  
'''

class GoodMorningException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class AudioException(GoodMorningException):
    def __init__(self, message):
        GoodMorningException.__init__(self, message)    
        
class DisplayException(GoodMorningException):
    def __init__(self, message):
        
        GoodMorningException.__init__(self, message)        
class AlarmException(GoodMorningException):
    def __init__(self, message):
        GoodMorningException.__init__(self, message)     

class SchedulerException(GoodMorningException):
    def __init__(self, message):
        GoodMorningException.__init__(self, message)    

class DispatcherException(GoodMorningException):
    def __init__(self, message):
        GoodMorningException.__init__(self, message)    

class Event(object):
    '''
    PyGame has this great thing where they use magic values
    to queue all events into one big queue. And users are kindly
    allowed to create custom events in a certain range. Screw them.
    '''
    SOUND_ENDED = pygame.locals.USEREVENT + 1
    KEYSTROKE = pygame.locals.USEREVENT + 100 # can't be +2, since we use SOUND_ENDED + n to broadcast that channel n has ended a sound

class EventDispatcher(object):
    '''
    Listener-like dispatcher for arbitrary events.
    Has a list of listeners one can register to.
    Each dispatcher expects all of its listeners
    to have a certain method it dispatches events to.
    '''
    def __init__(self, notify_method):
        self._listeners = []
        self._notify_method = notify_method
        
    def add_listener(self, listener):
        if not hasattr(listener, self._notify_method):
            raise DispatcherException("Listener of type '%s' does not offer a method named '%s'", (type(listener), self._notify_method))
        self._listeners.append(listener)
        
    def remove_listener(self, listener):
        self._listeners.remove(listener)
        
    def dispatch(self, event):
        for l in self._listeners:
            getattr(l, self._notify_method)(event)

class PygameEventListener(Thread):
    DELAY = 0.1
    
    def __init__(self):
        Thread.__init__(self, target = self.listen)
        self.running = False
        self.dispatcher = EventDispatcher("on_pygame_event")
        pygame.init()
        
    def stop(self):
        self.running = False
        
    def listen(self):
        self.running = True
        while self.running:
            try:
                for e in pygame.event.get():
                    self.dispatcher.dispatch(e)
            except:
                # make sure the loop keeps running even if pygame errors out!
                # Errors may occur due to not having any actualy display.
                # But that would skip shutdown routines
                # FIXME: dispatch as special event?
                pass 
            time.sleep(PygameEventListener.DELAY) # not sleeping led to weird segfaults
            
PygameEventListenerSingleton = PygameEventListener()
pygame.init()
PygameEventListenerSingleton.start()

