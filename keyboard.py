import sys
import tty
import termios
import warnings
import pygame
import util

from threading import Thread
from select import select

'''
Catches raw input from the keyboard for characters
and distributes that information via listener pattern.

This is required to support headless systems.
Pygame only catches keystrokes when a display is present.
While providing a dummy display, keystrokes can not
be caught as an event.
This module kind of works around this issue.

version: 1.0
author: Daniel O'Grady  
'''

class DummyKeyboard(object):
    def stop(self):
        pass

class RawInputWrapper(Thread):
    '''
    While running, this class will poll the std input every second.
    It will then attempt to read 1 character of input and distribute
    it to every class inside the self.listeners-list.
    Listeners are expected to have a method on_keydown(ch)
    where ch is the one character.
    Not having such a method will result in a warning but nothing else
    will happen!
    '''
    
    POLL_DELAY = 1
    def __init__(self):
        Thread.__init__(self, target = self.listen)
        fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(fd)
        self.listeners = []
        tty.setraw(fd)
    
    def stop(self):
        self.running = False
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSANOW, self.old_settings)
 
    def listen(self):
        self.running = True
        while self.running:
            rlist, _, _ = select([sys.stdin], [], [], RawInputWrapper.POLL_DELAY)
            if rlist:
                ch = sys.stdin.read(1)
                for l in self.listeners:
                    try:
                        l.on_keydown(ch)
                    except AttributeError:
                        warnings.warn('Class "%s" does not supply on_keydown(ch) method. Skipping silently.' % (l.__class__.__name__), RuntimeWarning)
        
class PygameKeyboardEventGenerator(object):
    def on_keydown(self, ch):
        e = pygame.event.Event(util.Event.KEYSTROKE, message=ch)
        pygame.event.post(e)
