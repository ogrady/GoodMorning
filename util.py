import pygame
import time
import functools
from pygame import locals
from threading import Thread
from enum import Enum


'''
Utility classes and exceptions.

version: 1.0
author: Daniel O'Grady  
'''

DEVELOPMENT = True

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
        
class Singleton:
    '''
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.
    
    This is more or less taken from 
    https://stackoverflow.com/a/7346105
    '''

    def __init__(self, decorated):
        self._decorated = decorated

    @property
    def instance(self):
        '''
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        '''
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
        
class Event(Enum):
    '''
    PyGame has this great thing where they use magic values
    to queue all events into one big queue. And users are kindly
    allowed to create custom events in a certain range. Screw them.
    '''
    KEYSTROKE = pygame.locals.USEREVENT + 1
    SOUND_ENDED = pygame.locals.USEREVENT + 2
    
    
# This is a special kind of stupid!
# While PyGame allows custom event types, they require you
# to be between their reserved values USEREVENT and NUMEVENTS,
# which gives you 9 values in total.
# But sometimes you have no choice but to identify the source
# of an event via the event-type-id (mixer.set_endevent).
# So here you go. Making sure all our constants are valid,
# looking forward to conflicting constant values when a user
# chooses use more than 5 channels... smh
# FIXME: incorporate maximum channels in Scene.__init__
assert reduce((lambda o,n: o and n), map(lambda x: pygame.locals.USEREVENT < x < pygame.locals.NUMEVENTS, [e.value for e in Event]), True) , "all user events must be between USEREVENT (%d) and NUMEVENTS (%d)" % (pygame.locals.USEREVENT, pygame.locals.NUMEVENTS)

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
            raise DispatcherException("Listener of type '%s' does not offer a method named '%s'" % (type(listener), self._notify_method))
        self._listeners.append(listener)
        
    def remove_listener(self, listener):
        self._listeners.remove(listener)
        
    def clear_listeners(self):
        self._listeners = []
        
    def dispatch(self, event):
        for l in self._listeners:
            getattr(l, self._notify_method)(event)

@Singleton
class PygameEventListener(object):
    def __init__(self):
        TimeTicker.instance.dispatcher.add_listener(self)
        self.running = True
        self.dispatcher = EventDispatcher("on_pygame_event")
        pygame.init()
        
    def on_tick(self, elapsed):
        try:
            for e in pygame.event.get():
                self.dispatcher.dispatch(e)
        except:
            # make sure the loop keeps running even if pygame errors out!
            # Errors may occur due to not having any actualy display.
            # But that would skip shutdown routines
            # FIXME: dispatch as special event?
            pass 
        
    def stop(self):
        if self.running:
            self.dispatcher.clear_listeners()
            TimeTicker.instance.dispatcher.remove_listener(self)
        

@Singleton
class TimeTicker(Thread):
    def __init__(self, delay = 0.5):
        Thread.__init__(self, target = self.tick)
        self.delay = delay
        self.running = False
        self.dispatcher = EventDispatcher("on_tick")
        self.start()
        
    def stop(self):
        if self.running:
            self.dispatcher.clear_listeners()
            self.running = False
        
    def tick(self):
        self.running = True
        timestamp = time.time()
        while self.running:
            time.sleep(self.delay)
            now = time.time()
            self.dispatcher.dispatch(now - timestamp)
            timestamp = now
        
pygame.init()

