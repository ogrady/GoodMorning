# -*- coding: utf-8 -*-

'''
This module is currently horribly overloaded
and should be split into:

    * Display
    * Audio
    * Error
    * Logic

version: 1.0
author: Daniel O'Grady  
'''

from threading import Thread
import time
import random
import schedule

import pygame

import audio
import display
import util
class GoodMorning(object):
    def quit(self):
        trans.stop()
        pygame.quit()
    
    def __init__(self):
        pygame.mixer.pre_init(frequency = 44100, size = -16, channels = 3)
        pygame.init()
        pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.am = audio.AudioMixer(sound_dir = "birds", ambient_dir = "ambient")
        dimensions = (0,0)
        dimensions = (400,200)
        disp = pygame.display.set_mode(dimensions,0,32)
        # enabling the following line is crucial for having a proper visual experience
        # but also ruins your day since there is no way to kill the program yet
        #pygame.display.toggle_fullscreen() 
        self.trans = display.Sunrise(disp)
        
    def start(self):
        self.trans.start()
        self.am.start() # mix() instead of start()?

        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type >= util.Event.SOUND_ENDED and e.type <= util.Event.SOUND_ENDED + len(self.am.sound_chans):
                    self.am.next_sound(e.type - util.Event.SOUND_ENDED)
                else:
                    pass
            pygame.display.update()
        quit()  

def main():
    GoodMorning().start()
    """s = Scheduler()
    a1 = Alarm(21,21)
    s.add_alarm(a1)
    print(s.jobs)
    s.remove_alarm(0)
    print(s.jobs)
    s.remove_alarm(0)
    s.start()
    """

main()