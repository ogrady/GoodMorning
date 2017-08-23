import pygame
from pygame import locals

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

class Event(object):
    '''
    PyGame has this great thing where they use magic values
    to queue all events into one big queue. And users are kindly
    allowed to create custom events in a certain range. Screw them.
    '''
    SOUND_ENDED = pygame.locals.USEREVENT + 1