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
import os
import functools
import random

from pygame import mixer, display, draw, locals
import pygame

class GoodMorningException(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class AudioException(GoodMorningException):
	def __init__(self, message):
		GoodMorningException.__init__(self, message)	
		
class DisplayException(GoodMorningException):
	def __init__(self, message):
		GoodMorningException.__init__(self, message)		

class Event(object):
	'''
	PyGame has this great thing where they use magic values
	to queue all events into one big queue. And users are kindly
	allowed to create custom events in a certain range. Screw them.
	'''
	SOUND_ENDED = pygame.locals.USEREVENT + 1


class ColourTransition(Thread):
	'''
	Transists the background colour of a GUI from black to white in discrete steps.
	'''	
	@property
	def hex(self):
		'''
		Hex version of self.rgb, string with preceding diamond.
		(No longer needed since migration to PyGame)
		'''
		rgbh = map(lambda c: hex(c)[2:], self.rgb)
		r,g,b = map(lambda c: c if len(c) > 1 else "0%s" % (c,), rgbh)
		return "#%s%s%s" % (r,g,b)
		
	def stop(self):
		'''
		Stops the run gracefully.
		If the transition is currently not running this does nothing.
		'''
		self.running = False
	
	def __init__(self, display, rd = lambda x:1, gd = lambda x:1, bd = lambda x:1, rmax = 255, gmax = 255, bmax = 255, sleep = 0.5, init = (0,0,0)):
		'''
		gui: display for which to fill the colour
		rd: red delta-function for each step
		gd: green delta-function for each step
		bd: blue delta-function for each step
		rmax: max for red (255 boundary not checked)
		gmax: max for green (255 boundary not checked)
		bmax: max for blue (255 boundary not checked)
		sleep: sleep time between each step in seconds
		'''
		Thread.__init__(self, target = self.transit)
		self.display = display
		self.init = init
		self.rgb = init
		self.rd = rd
		self.gd = gd
		self.bd = bd
		self.rmax = rmax
		self.gmax = gmax
		self.bmax = bmax
		self.sleep = sleep

	def next(self):
		'''
		Calculates the next step based on the deltas.
		Each component is capped at 255.
		'''
		r,g,b = self.rgb
		r = min(self.rmax,(r+self.rd(r)))
		g = min(self.gmax,(g+self.gd(g)))
		b = min(self.bmax,(b+self.bd(b)))
		self.rgb = (r,g,b)
		
	def transit(self):
		'''
		Does all transition steps until explicitely
		stopped via self.stop().
		'''
		self.running = True
		self.rgb = self.init
		while self.running:
			self.next()
			self.display.fill(self.rgb)
			time.sleep(self.sleep)	

class Sunrise(ColourTransition):
	def __init__(self, gui):
		ColourTransition.__init__(self, gui
			, rd = lambda x:7
			, gd = lambda x:2
			, bd = lambda x:2
			, gmax = 220
			, bmax = 220
			, sleep = 0.5
			)

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
		mixer.init(channels = channels)
		self.ambient_chan = mixer.Channel(0)
		self.sound_chans = [mixer.Channel(i) for i in range(1,channels)]
		self.ambient_chan.set_endevent(Event.SOUND_ENDED)
		for i in range(0, len(self.sound_chans)):
			self.sound_chans[i].set_endevent(Event.SOUND_ENDED + i)
	
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
		s = mixer.Sound(random.choice(self.sounds))
		self.sound_chans[channel].play(s, fade_ms = fade_ms)
		
	def next_ambient(self, fade_ms = 10000):
		'''
		Plays a random ambient, looping forever.
		'''
		s = mixer.Sound(random.choice(self.ambients))
		self.ambient_chan.play(s, loops = -1, fade_ms = fade_ms)

	def mix(self):
		'''
		Plays a random, looping ambient and a
		random effect in each effect channel.
		'''
		self.next_ambient()
		for i in range(0, len(self.sound_chans)):
			self.next_sound(channel = i)
			
class GoodMorning(object):
	def quit(self):
		trans.stop()
		pygame.quit()
	
	def __init__(self):
		pygame.init()
		pygame.display.set_mode((0,0),pygame.FULLSCREEN)
		self.am = AudioMixer(sound_dir = "birds", ambient_dir = "ambient")
		dimensions = (0,0)
		dimensions = (400,200)
		display=pygame.display.set_mode(dimensions,0,32)
		# enabling the following line is crucial for having a proper visual experience
		# but also ruins your day since there is no way to kill the program yet
		#pygame.display.toggle_fullscreen() 
		self.trans = Sunrise(display)
		
	def start(self):
		self.trans.start()
		self.am.mix()

		running = True
		while running:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					running = False
				elif e.type >= Event.SOUND_ENDED and e.type <= Event.SOUND_ENDED + len(self.am.sound_chans):
					self.am.next_sound(e.type - Event.SOUND_ENDED)
				else:
					pass
			pygame.display.update()
		quit()			
		
def main():
	GoodMorning().start()


main()