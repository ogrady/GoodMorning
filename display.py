from threading import Thread
import time

'''
Display components for controlling
a standard HDMI display.

version: 1.0
author: Daniel O'Grady  
'''

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
    
    def show(self):
        '''
        Displays the current state of the transition.
        '''
        self.display.fill(self.rgb)
        
    def transit(self):
        '''
        Does all transition steps until explicitely
        stopped via self.stop().
        '''
        self.running = True
        self.rgb = self.init
        while self.running:
            self.next()
            self.show()
            time.sleep(self.sleep)  

class Sunrise(ColourTransition):
    def __init__(self, display):
        ColourTransition.__init__(self, display
            , rd = lambda x:7
            , gd = lambda x:2
            , bd = lambda x:2
            , gmax = 220
            , bmax = 220
            , sleep = 0.5
            )

class LEDProto(Sunrise):
    LED_size = 10
    LED_space = 5
    
    import pygame
    
    def __init__(self, led_count = 100):
        Sunrise.__init__(self, display = None)
        # pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        dimensions = (LEDProto.LED_size, 20 + led_count * LEDProto.LED_size)
        self.display = LEDProto.pygame.display.set_mode(dimensions,0,32)
        self.leds = [(0,0,0)] * led_count
        
    def set(self, index, r, g, b):
        self.leds[index] = (r,g,b)
        
    def next(self):
        r,g,b = self.rgb
        
        r = min(self.rmax,(r+self.rd(r)))
        g = min(self.gmax,(g+self.gd(g)))
        b = min(self.bmax,(b+self.bd(b)))
        for i in range(len(self.leds)):
            self.set(i,r,g,b)
        self.rgb = (r,g,b)
        
    def show(self):
        self.display.fill((0,0,0))
        for i in range(len(self.leds)):
            s = LEDProto.LED_size
            LEDProto.pygame.draw.ellipse(
                self.display,
                self.leds[i],
                LEDProto.pygame.Rect(0, s * i + LEDProto.LED_space * i, s, s),
                0
            )

class LED(Sunrise):
    # Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
    import time
    import RPi.GPIO as GPIO
     
    # Import the WS2801 module.
    import Adafruit_WS2801 as Strip
    import Adafruit_GPIO.SPI as SPI
    
    def __init__(self, led_count = 100):
        Sunrise.__init__(self, display = None)
        # self.leds = [(0,0,0)] * led_count
        pixels.clear()
        pixels.show()
    
    def next(self):
        r,g,b = self.rgb
        
        r = min(self.rmax,(r+self.rd(r)))
        g = min(self.gmax,(g+self.gd(g)))
        b = min(self.bmax,(b+self.bd(b)))
        for i in range(pixels.count()):
            pixels.set_pixel(i, (r,g,b))
        self.rgb = (r,g,b)
        
    def show(self):
        pixels.show()
