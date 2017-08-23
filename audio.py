from threading import Thread
import os
import random
import pygame as pg
import util

'''
Audio components.

version: 1.0
author: Daniel O'Grady  
'''

class AudioMixer(Thread):
    '''
    Mixes ambient and effect sounds, where ambient
    sounds actually loop indefinitely while effects
    are just queued. There can be multiple effect channels
    to create a cacophony of effects for when you just really
    can't get out of bed...
    '''
    def __init__(self, basedir = ".", sound_dir = "sounds", ambient_dir = "ambient", channels = 3):
        '''
        Constructor
        basedir: lowest common ancestor of sound_dir and ambient_dir
        sound_dir: subdirectory in which effect sounds are stored
        ambient_dir: subdirectory in which ambient sounds are stored
        channels: channel count. First channel is always for ambient, all further channels are for effects
        '''
        if channels < 2:
            raise AudioException("Invalid channel count '%s', expected at least 2 channels" % (channels,))
        Thread.__init__(self, target = self.mix)
        self.ambients = self.load_sounds("/".join((basedir, ambient_dir)))
        self.sounds = self.load_sounds("/".join((basedir, sound_dir)))
        pg.mixer.init(channels = channels)
        self.ambient_chan = pg.mixer.Channel(0)
        self.sound_chans = [pg.mixer.Channel(i) for i in range(1,channels)]
        self.ambient_chan.set_endevent(util.Event.SOUND_ENDED)
        for i in range(0, len(self.sound_chans)):
            self.sound_chans[i].set_endevent(util.Event.SOUND_ENDED + i)
    
    def load_sounds(self, dir, extensions = (".ogg", ".wav")):
        '''
        Loads all files with the passed extension
        from a directory and attempty to load them
        as audio files, which is the resulting list.
        '''
        sounds = list(map(lambda f: "%s/%s" % (dir, f), [f for f in os.listdir(dir) if f.endswith(extensions)]))
        if not sounds:
            raise AudioException("No audio files could be loaded from '%s' with extensions %s" % (dir,extensions))
        return sounds
        
    def next_sound(self, channel = 0, fade_ms = 1000):
        '''
        Plays the next random sound in the
        given channel.
        '''
        if not (0 <= channel < len(self.sound_chans)):
            raise AudioException("Invalid channel %s, must be between 0 and %s" % (channel,len(self.sound_chans)))
        s = pg.mixer.Sound(random.choice(self.sounds))
        self.sound_chans[channel].play(s, fade_ms = fade_ms)
        
    def next_ambient(self, fade_ms = 10000):
        '''
        Plays a random ambient, looping forever.
        '''
        s = pg.mixer.Sound(random.choice(self.ambients))
        self.ambient_chan.play(s, loops = -1, fade_ms = fade_ms)

    def mix(self):
        '''
        Plays a random, looping ambient and a
        random effect in each effect channel.
        '''
        self.next_ambient()
        for i in range(0, len(self.sound_chans)):
            self.next_sound(channel = i)