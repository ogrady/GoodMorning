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
import logger as l

import sys
import getopt

class GoodMorning(object):
    DT_LED = 11
    DT_LED_PROTO = 12
    DT_SUNRISE = 13
    
    AT_MIXER = 21
    AT_MUTE = 22
    
    def quit(self):
        l.log("Stopping GoodMorning as requested")
        self.keyboard.stop()
        util.PygameEventListener.instance.stop()
        util.TimeTicker.instance.stop()
        pygame.quit()
        l.Logger.instance.close()
    
    def __init__(self, config_file):
        pygame.mixer.pre_init(frequency = 44100, size = -16, channels = 3)
        pygame.init()
        # self.keyboard = keyboard.DummyKeyboard()
        self.keyboard = keyboard.RawInputWrapper()
        self.keyboard.dispatcher.add_listener(keyboard.PygameKeyboardEventGenerator())

        # Alarms init
        self.alarm_scheduler = config.read_alarms(config_file)
        
    def start(self):
        l.log("Booting GoodMorning")
        util.PygameEventListener.instance.dispatcher.add_listener(self)
        self.keyboard.start()
        self.alarm_scheduler.start()
        
    def on_pygame_event(self, e):
        if e.type == pygame.QUIT:
            self.quit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.quit()
        if e.type == util.Event.KEYSTROKE and e.message == 'q':
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
    GoodMorning('config.json').start()

if __name__ == "__main__":
    main(sys.argv[1:])
