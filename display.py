from threading import Thread
import time
import os
import pygame
import Adafruit_WS2801 as Strip
import Adafruit_GPIO.SPI as SPI

import util

'''
Display components for controlling
a standard HDMI display.

version: 1.0
author: Daniel O'Grady  
'''

class ColourTransition(object):
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
        
    def start(self):
        '''
        Starts the transition.
        '''
        util.TimeTicker.instance.dispatcher.add_listener(self)
        
    def stop(self):
        '''
        Stops the run gracefully.
        If the transition is currently not running this does nothing.
        '''
        util.TimeTicker.instance.dispatcher.remove_listener(self)
        self.rgb = self.init
        self.elapsed = 0
        self.clear()
        self.show()

    
    def __init__(self, display, rd = lambda x:0, gd = lambda x:0, bd = lambda x:0, rmin = 0, gmin = 0, bmin = 0, rmax = 255, gmax = 255, bmax = 255, sleep = 0.5, init = (0,0,0)):
        '''
        gui: display for which to fill the colour
        rd: red delta-function for each step
        gd: green delta-function for each step
        bd: blue delta-function for each step
        rmin: min for red
        gmin: min for green
        bmin: min for blue
        rmax: max for red
        gmax: max for green
        bmax: max for blue
        sleep: sleep time between each step in seconds
        init: initial rgb tuple
        '''
        self.display = display
        self.init = init
        self.rgb = init
        self.rd = rd
        self.gd = gd
        self.bd = bd
        self.rmin = rmin
        self.gmin = gmin
        self.bmin = bmin
        self.rmax = rmax
        self.gmax = gmax
        self.bmax = bmax
        self.sleep = sleep
        self.elapsed = 0

    def next(self):
        '''
        Calculates the next step based on the deltas.
        Each component is capped between the respective min and max.
        '''
        r,g,b = self.rgb
        r = max(self.rmin, min(self.rmax,(r+self.rd(r))))
        g = max(self.gmin, min(self.gmax,(g+self.gd(g))))
        b = max(self.bmin, min(self.bmax,(b+self.bd(b))))
        
        assert 0 <= r <= 255, "invalid red value"
        assert 0 <= g <= 255, "invalid green value"
        assert 0 <= b <= 255, "invalid blue value"
        self.rgb = (r,g,b)
    
    def show(self):
        '''
        Displays the current state of the transition.
        '''
        self.display.fill(self.rgb)
        
    def clear(self):
        '''
        Clears the display (without showing it)
        '''
        pass
        
    def on_tick(self, elapsed):
        self.elapsed += elapsed
        if self.elapsed >= self.sleep:
            self.next()
            self.show()
            self.elapsed = 0

class LEDProto(ColourTransition):
    LED_size = 10
    LED_space = 5
    
    import pygame
    
    def __init__(self, rd, gd, bd, rmin, gmin, bmin, rmax, gmax, bmax, sleep = 0.5, led_count = 100, init = (0,0,0)):
        ColourTransition.__init__(self, None
            , rd = lambda x:rd
            , gd = lambda x:gd
            , bd = lambda x:bd
            , rmin = rmin
            , gmin = gmin
            , bmin = bmin
            , rmax = rmax
            , gmax = gmax
            , bmax = bmax
            , sleep = sleep
            , init = init
            )
        # pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        dimensions = (LEDProto.LED_size, 20 + led_count * LEDProto.LED_size)
        self.display = LEDProto.pygame.display.set_mode(dimensions,0,32)
        self.leds = [(0,0,0)] * led_count
        
    def set(self, index, r, g, b):
        self.leds[index] = (r,g,b)
        
    def next(self):
        ColourTransition.next(self)
        r,g,b = self.rgb
        for i in range(len(self.leds)):
            self.set(i,r,g,b)
        
    def show(self):
        self.clear()
        for i in range(len(self.leds)):
            s = LEDProto.LED_size
            LEDProto.pygame.draw.ellipse(
                self.display,
                self.leds[i],
                LEDProto.pygame.Rect(0, s * i + LEDProto.LED_space * i, s, s),
            )
        pygame.display.update()
            
    def clear(self):
        self.display.fill((0,0,0))
        
    def stop(self):
        r,g,b = (0,0,0)
        for i in range(len(self.leds)):
            self.set(i,r,g,b)
        ColourTransition.stop(self)

class LED(ColourTransition):
    def __init__(self, rd, gd, bd, rmin, gmin, bmin, rmax, gmax, bmax, sleep = 0.5, led_count = 32, spi_port = 0, spi_device = 0, init = (0,0,0)):
        import RPi.GPIO as GPIO # must remain in constructor to only trigger error upon instantiating!
        
        ColourTransition.__init__(self, None
            , rd = lambda x:rd
            , gd = lambda x:gd
            , bd = lambda x:bd
            , rmin = rmin
            , gmin = gmin
            , bmin = bmin
            , rmax = rmax
            , gmax = gmax
            , bmax = bmax
            , sleep = sleep
            , init = init
            )
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.init()
        self.pixels = Strip.WS2801Pixels(led_count, spi=SPI.SpiDev(spi_port, spi_device), gpio=GPIO)
        self.pixels.clear()
        self.pixels.show()
        
    def set(self, index, r, g, b):
        self.pixels.set_pixel(index, Strip.RGB_to_color(b,g,r))
    
    def next(self):
        ColourTransition.next(self)
        r,g,b = self.rgb
        for i in range(self.pixels.count()):
            self.set(i, r,g,b)
        
    def show(self):
        self.pixels.show()
        
    def clear(self):
        self.pixels.clear()

class LEDWatchdog(object):
    def __init__(self, led):
        self.led = led
        self.something_ringing = False
    
    def on_ringing_change(self, event):
        self.something_ringing = event["new"] > 0
        
    def on_tick(self, delta):
        if self.something_ringing:
            led.clear()
            print("clearing")
        else:
            print("not")
