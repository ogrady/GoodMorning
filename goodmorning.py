# -*- coding: utf-8 -*-

'''
Main module.

version: 1.0
author: Daniel O'Grady  
'''

from threading import Thread
import time
import random
import alarm

import pygame

import audio
import display
import util
import keyboard
import config


import sys
import getopt

class GoodMorning(object):
    DT_LED = 11
    DT_LED_PROTO = 12
    DT_SUNRISE = 13
    
    AT_MIXER = 21
    AT_MUTE = 22
    
    def quit(self):
        self.trans.stop()
        self.keyboard.stop()
        pygame.quit()
    
    def __init__(self, display_type, audio_type):
        pygame.mixer.pre_init(frequency = 44100, size = -16, channels = 3)
        pygame.init()
        self.keyboard = keyboard.DummyKeyboard()
        dimensions = (0,0)
        dimensions = (400,200)
        
        # Display init
        if display_type == GoodMorning.DT_LED:
            self.trans = display.LED()
            self.keyboard = keyboard.RawInputWrapper()
            self.keyboard.listeners.append(keyboard.PygameKeyboardEventGenerator())
            self.keyboard.start()
        elif display_type == GoodMorning.DT_LED_PROTO:
            self.trans = display.LEDProto()
        elif display_type == GoodMorning.DT_SUNRISE:
            pygame.display.set_mode((0,0),pygame.FULLSCREEN)
            disp = pygame.display.set_mode(dimensions,0,32)
            # enabling the following line is crucial for having a proper visual experience
            # but also ruins your day since there is no way to kill the program yet
            #pygame.display.toggle_fullscreen() 
            self.trans = display.Sunrise(disp)
        else:
            raise util.GoodMorningException('Unknown display transition "%s"' % (str(display_type)))
    
        # Audio init
        if audio_type == GoodMorning.AT_MIXER:
            self.am = audio.AudioMixer(sound_dir = "birds", ambient_dir = "ambient")
        elif audio_type == GoodMorning.AT_MUTE:
            audio.Mute()
        else:
            raise util.GoodMorningException('Unknown audio mixer "%s"' % (str(audio_type)))
        
    def start(self):
        self.trans.start()
        self.am.start() # mix() instead of start()?

        running = True
        while running:
            try:
                for e in pygame.event.get():
                    # print(e)
                    if e.type == pygame.QUIT:
                        running = False
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        running = False
                    if e.type == util.Event.KEYSTROKE and e.message == 'q':
                        running = False
                    elif e.type >= util.Event.SOUND_ENDED and e.type <= util.Event.SOUND_ENDED + len(self.am.sound_chans):
                        self.am.next_sound(e.type - util.Event.SOUND_ENDED)
                    else:
                        pass
                pygame.display.update()
            except:
                # make sure the loop keeps running even if pygame errors out!
                # Errors may occur due to not having any actualy display.
                # But that would skip past self.quit()
                pass 
            
        self.quit()  

def main(argv):
    
    import keyboard
    opts, args = getopt.getopt(argv,"hd:a:")
    
    for opt, arg in opts:
        if opt == '-d':
            d = {'led': GoodMorning.DT_LED,
                 'pled': GoodMorning.DT_LED_PROTO,
                 'sun': GoodMorning.DT_SUNRISE}[arg]
        if opt == '-a':
            a = {'mix': GoodMorning.AT_MIXER,
                 'mute': GoodMorning.AT_MUTE}[arg]
    GoodMorning(d,a).start()
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
    #s = config.read_alarms('config.json')
    #s.start()
    #pass
    #main(sys.argv[1:])
    print(config.read_sceneries('config.json'))
