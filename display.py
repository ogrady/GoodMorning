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