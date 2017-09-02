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

import sys
import getopt

class GoodMorning(object):
    T_LED = 1
    T_LED_PROTO = 2
    T_SUNRISE = 3
    
    def quit(self):
        self.trans.stop()
        pygame.quit()
    
    def __init__(self, t_type):
        pygame.mixer.pre_init(frequency = 44100, size = -16, channels = 3)
        pygame.init()
        self.am = audio.Mute() #audio.AudioMixer(sound_dir = "birds", ambient_dir = "ambient")
        dimensions = (0,0)
        dimensions = (400,200)
        if t_type == GoodMorning.T_LED:
            self.trans = display.LED()
        elif t_type == GoodMorning.T_LED_PROTO:
            self.trans = display.LEDProto()
        elif t_type == GoodMorning.T_SUNRISE:
            pygame.display.set_mode((0,0),pygame.FULLSCREEN)
            disp = pygame.display.set_mode(dimensions,0,32)
            # enabling the following line is crucial for having a proper visual experience
            # but also ruins your day since there is no way to kill the program yet
            #pygame.display.toggle_fullscreen() 
            self.trans = display.Sunrise(disp)
        else:
            raise util.GoodMorningException('Unknown display transition "%s"' % (str(t_type)))
        
    def start(self):
        self.trans.start()
        self.am.start() # mix() instead of start()?

        running = True
        while running:
            try:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        running = False
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        running = False
                    elif e.type >= util.Event.SOUND_ENDED and e.type <= util.Event.SOUND_ENDED + len(self.am.sound_chans):
                        self.am.next_sound(e.type - util.Event.SOUND_ENDED)
                    else:
                        pass
            except:
                # make sure the loop keeps running even if pygame errors out!
                # Errors may occur due to not having any actualy display.
                # But that would skip past self.quit()
                pass 
            pygame.display.update()
        self.quit()  

def main(argv):
    opts, args = getopt.getopt(argv,"hd:x:")
    
    for opt, arg in opts:
        if opt == '-d':
            d = {'led': GoodMorning.T_LED,
                 'pled': GoodMorning.T_LED_PROTO,
                 'sun': GoodMorning.T_SUNRISE}[arg]
    GoodMorning(d).start()
    """s = Scheduler()
    a1 = Alarm(21,21)
    s.add_alarm(a1)
    print(s.jobs)
    s.remove_alarm(0)
    print(s.jobs)
    s.remove_alarm(0)
    s.start()
    """

if __name__ == "__main__":
   main(sys.argv[1:])
