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
import atexit

class GoodMorning(object):
    DT_LED = 11
    DT_LED_PROTO = 12
    DT_SUNRISE = 13
    
    AT_MIXER = 21
    AT_MUTE = 22
    
    def quit(self):
        if self.running:
            self.running = False
            l.log("Stopping GoodMorning as requested")
            self.keyboard.stop()
            self.alarm_scheduler.stop()
            util.PygameEventListener.instance.stop()
            util.TimeTicker.instance.stop()
            pygame.quit()
            l.Logger.instance.close()
            exit()
    
    def __init__(self, config_file):
        self.running = False
        pygame.mixer.pre_init(frequency = 44100, size = -16, channels = 3)
        pygame.init()
        # self.keyboard = keyboard.DummyKeyboard()
        self.keyboard = keyboard.RawInputWrapper()
        self.keyboard.dispatcher.add_listener(keyboard.PygameKeyboardEventGenerator())

        # Alarms init
        self.alarm_scheduler = config.read_alarms(config_file)
        
    def start(self):
        atexit.register(self.quit)
        self.running = True
        l.log("Starting GoodMorning")
        util.PygameEventListener.instance.dispatcher.add_listener(self)
        self.keyboard.start()
        self.alarm_scheduler.start()
        
    def on_pygame_event(self, e):
        # l.log("Received event " + str(e))
        if e.type == pygame.QUIT:
            l.log("Received termination request")
            self.quit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            l.log("Received esc Keystroke")
            self.quit()
        if e.type == util.Event.KEYSTROKE.value and e.message == 'q':
            l.log("Received q Keystroke")
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
    try:
        dev_mode = config.read_config_value(util.CONFIG_FILE, "general", "development", util.C_DEVELOPMENT)
        gm = GoodMorning(util.ALARMS_FILE)
        gm.start()
        if dev_mode:
            # start the first alarm upon start for debugging!
            gm.alarm_scheduler.alarms[0].ring()
    except Exception as ex:
        print(type(ex))
        l.log("Top level error: " + str(ex), l.T_ERROR)
        print("Caught toplevel error '%s'. See logfile %s for more info" % (str(ex), util.LOG_FILE))

if __name__ == "__main__":
    main(sys.argv[1:])
