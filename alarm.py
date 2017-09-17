import schedule
import time 
import functools
import util
import pygame
from threading import Thread

'''
Everything related to scheduling
events in a cron-like fashion.

version: 1.0
author: Daniel O'Grady  
'''
class Scheduler(Thread):
    @property
    def jobs(self):
        return self._scheduler.jobs

    def __init__(self, delay = 60):
        # sleep: interval in seconds in which the Scheduler checks for pending jobs
        Thread.__init__(self, target = self.run)
        self._scheduler = schedule.Scheduler()
        self.running = False
        self.delay = delay

    def stop(self):
        self.running = False

    def add_alarm(self, alarm):
        '''
        Adds an alarm on each of the alarms days on their time.
        Note: leaving days empty results in the alarm ringing
        every day!
        '''
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

    def remove_alarm(self, index):
        if index >= len(self._scheduler.jobs):
            raise SchedulerException("Invalid index %d" % (index))
        self._scheduler.cancel_job(self._scheduler.jobs[index])

    def run(self):
        self.running = True
        while self.running:
            self._scheduler.run_pending()
            time.sleep(self.delay)

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
        
    @minute.setter
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
        
    def ring(self):
        '''
        Action to take when this alarm rings.
        '''
        pass
        print("RING RING")
        print(self.string)
        
    def turn_off(self):
        '''
        Shutdown action for the rining alarm.
        '''
        pass

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
        self.scenery = scenery
        

class Scenery(object):
    def __init__(self, name, sounds):
        self.name = name
        self.channels = []
        for s in sounds:
            self.channels.append(s)
            
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

class SceneryAlarm():
    def __init__(self, hour, minute = 0, second = 0, days = [], name = '', scenery = None):
        Alarm.__init__(self, hour = hour, minute = minute, second = second, days = days, name = name)
        self.scenery = scenery
        
    def ring(self):
        running = True
        while running:
            pass
            
