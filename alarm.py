import schedule
import time 
import functools
import util
import pygame
import logger as l
import util

import display
import audio

'''
Everything related to scheduling
events in a cron-like fashion.

version: 1.0
author: Daniel O'Grady  
'''
class Scheduler(object):
    @property
    def jobs(self):
        return self._scheduler.jobs

    # FIXME: reset default sleep to 60
    def __init__(self, sleep = 1):
        # sleep: interval in seconds in which the Scheduler checks for pending jobs
        self._scheduler = schedule.Scheduler()
        self.sleep = sleep
        self.elapsed = 0
        self.alarms = []
        self.dispatcher = util.EventDispatcher("on_ringing_change")
        self.ringing_alarms = 0
        
    def on_alarm_state_change(self, event):
        old = self.ringing_alarms
        if event["ringing"]:
            self.ringing_alarms += 1
        else:
            self.ringing_alarms -= 1
        self.dispatcher.dispatch({"old": old, "new": self.ringing_alarms})
        
    def start(self):
        util.TimeTicker.instance.dispatcher.add_listener(self)

    def stop(self):
        util.TimeTicker.instance.dispatcher.remove_listener(self)
        self._scheduler.clear()
        [a.turn_off() for a in self.alarms if a.ringing]
        self.alarms = []

    def add_alarm(self, alarm):
        '''
        Adds an alarm on each of the alarms days on their time.
        Note: leaving days empty results in the alarm ringing
        every day!
        '''
        l.log("Scheduling %s" % (str(alarm),))
        if alarm.days:
            for d in alarm.days:
                ev = self._scheduler.every()
                if d == Alarm.MONDAY:
                    act = ev.monday
                elif d == Alarm.TUESDAY:
                    act = ev.tuesday
                elif d == Alarm.WEDNESDAY:
                    act = ev.wednesday
                elif d == Alarm.THURSDAY:
                    act = ev.thursday
                elif d == Alarm.FRIDAY:
                    act = ev.friday
                elif d == Alarm.SATURDAY:
                    act = ev.saturday
                elif d == Alarm.SUNDAY:
                    act = ev.sunday
                act.at(alarm.string).do(alarm.ring)
        else:
            self._scheduler.every().day.at(alarm.string).do(alarm.ring)
        self.alarms.append(alarm)
        alarm.dispatcher.add_listener(self)

    def remove_alarm(self, index):
        if index >= len(self._scheduler.jobs):
            raise SchedulerException("Invalid index %d" % (index))
        self._scheduler.cancel_job(self._scheduler.jobs[index])
        alarm.dispatcher.remove_listener(self)

    def on_tick(self, elapsed):
        self.elapsed += elapsed
        if self.elapsed > self.sleep:
            self._scheduler.run_pending()
            self.elapsed = 0

class Alarm(object):
    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'
    SUNDAY = 'sun'
    DAYS = [  MONDAY
            , TUESDAY
            , WEDNESDAY
            , THURSDAY
            , FRIDAY
            , SATURDAY
            , SUNDAY
           ]
    
    '''
    Encapsulation for an alarm event.
    '''
    @property
    def string(self):
        return "%d:%d" % (self.hour, self.minute)

    @property
    def hour(self):
        return self._hour

    @hour.setter
    def hour(self, value):
        if not (0 <= value < 23):
            raise util.AlarmException("Invalid hour: %d" % (value,))
        self._hour = value

    @property
    def minute(self):
        return self._minute
        
    @minute.setter
    def minute(self, value):
        if not (0 <= value < 59):
            raise util.AlarmException("Invalid minute: %d" % (value,))
        self._minute = value
        
    @property
    def second(self):
        return self._second
        
    @second.setter
    def second(self, value):
        if not (0 <= value < 59):
            raise util.AlarmException("Invalid second: %d" % (value,))
        self._second = value
        
    @property
    def days(self):
        return self._days
        
    @days.setter
    def days(self, values):
        if not functools.reduce(lambda v,n: v and (n in Alarm.DAYS), values, True):
            raise util.AlarmException("Invalid weekday value in: %s" % (str(values),))
        self._days = values
        
        
    @property
    def ringing(self):
        return self._ringing
        
    @ringing.setter
    def ringing(self, value):
        self._ringing = value
        self.dispatcher.dispatch({"alarm": self, "ringing": value})
        
    def ring(self):
        '''
        Action to take when this alarm rings.
        '''
        self.ringing = True
        
    def turn_off(self):
        '''
        Shutdown action for the rining alarm.
        '''
        self.ringing = False

    def __init__(self, hour, minute = 0, second = 0, days = [], name = ''):
        '''
        hour: hour on which to run the alarm
        minute: minute on which to run the alarm
        second: second on which to run the alarm
        days: days on which to run the alarm
        name: name of the alarm
        scenery: Scenery object
        '''
        self.name = name
        self.hour = hour
        self.minute = minute
        self.second = second
        self.days = days
        self._ringing = False
        self.dispatcher = util.EventDispatcher("on_alarm_state_change")
        
    def __str__(self):
        return "'%s' on %d:%d:%d, %s" % (self.name, self.hour, self.minute, self.second, self.days)

class Scenery(object):
    def __init__(self, name, sounds, rd, gd, bd, rmin, gmin, bmin, rmax, gmax, bmax, sleep, init = (0,0,0)):
        self.name = name
        self.sleep = sleep
        try:
            self.display = display.LED(rd = rd, gd = gd, bd = bd,
                              rmin = rmin, gmin = gmin, bmin = bmin,
                              rmax = rmax, gmax = gmax, bmax = bmax,
                              sleep = sleep,
                              init = init)
            l.log("Initialised scenery '%s'" % (self.name,))
        except RuntimeError as e:
            if str(e) != 'This module can only be run on a Raspberry Pi!':
                # Nasty hack.
                # The LED module doesn't use a specific type of exception for
                # their environment check. To avoid catching unrelated RuntimeErrors,
                # we check the message string. This could lead to errors in
                # other version, where the message could have been altered!
                raise e
            # not running on RaspberryPi -> display the proto
            l.log("Detected dummy environment. Using LEDProto for scenery '%s' instead" % (self.name,))
            self.display = display.LEDProto(rd = rd, gd = gd, bd = bd,
                                               rmin = rmin, gmin = gmin, bmin = bmin,
                                               rmax = rmax, gmax = gmax, bmax = bmax,
                                               sleep = sleep, led_count = 100, init = init)

        self.audiomixer = audio.AudioMixer(sound_groups = sounds)
            
    def start(self):
        self.display.start()
        self.audiomixer.start()
        
    def stop(self):
        self.display.stop()
        self.audiomixer.stop()

class SceneryAlarm(Alarm):
    def __init__(self, hour, minute = 0, second = 0, days = [], name = '', scenery = None, duration = -1):
        Alarm.__init__(self, hour = hour, minute = minute, second = second, days = days, name = name)
        self.scenery = scenery
        self.duration = duration
        self.elapsed = 0
        
    def ring(self):
        if not self.ringing:
            l.log("Starting %s '%s' on %s" % (self.__class__.__name__, self.name, self.string))
            Alarm.ring(self)
            util.TimeTicker.instance.dispatcher.add_listener(self)
            self.scenery.start()
        
    def turn_off(self):
        if self.ringing:
            l.log("Turning off %s '%s'" % (self.__class__.__name__, self.name,))
            Alarm.turn_off(self)
            util.TimeTicker.instance.dispatcher.remove_listener(self)
            self.elapsed = 0
            self.scenery.stop()

    def on_tick(self, elapsed):
        if self.duration > 0: # <= 0 -> ring indefinitely
            self.elapsed += elapsed
            if self.elapsed >= self.duration:
                l.log("Alarm '%s' exceeded configured duration of %d seconds and is being turned off" % (self.name, self.duration))
                self.turn_off()

class SceneryLullaby(SceneryAlarm):
    def __init__(self, name, scenery = None, duration = -1):
        SceneryAlarm.__init__(self, hour = 0, minute = 0, second = 0, days = [], name = name, scenery = scenery, duration = duration)
        
lullabies = {}
