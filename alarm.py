import schedule
import time 
import json
import functools
import util
from threading import Thread

'''
Everything related to scheduling
events in a cron-like fashion.

version: 1.0
author: Daniel O'Grady  
'''
def read_alarms(file, scheduler = None):
    '''
    file: json file from which to read the alarms. They are expected to
          be in the format: 
          alarms: [
            name: .., (description OPTIONAL)
            hour: .., (hour)
            minute: .., (minute OPTIONAL)
            second: .., (second OPTIONAL)
            days: [..], (array of 'mon',..'sun' OPTIONAL, empty results in ringing every day)
            active: .., (boolean whether to ring OPTIONAL, defaults to true)
          ]
    scheduler: scheduler into which to load the alarms. If no scheduler
               is passed a new one will be created
    returns: the scheduler into which the alarms have been read
    '''
    if not scheduler:
        scheduler = Scheduler()
    with open(file) as fd:
        data = json.load(fd)
        for alarm_json in data['alarms']:
            # FIXME: typecheck!
            active = alarm_json['active'] if 'active' in alarm_json else True
            if active:
                name = alarm_json['name'] if 'name' in alarm_json else ''
                hour = alarm_json['hour'] # mandatory!
                minute = alarm_json['minute'] if 'minute' in alarm_json else 0
                second = alarm_json['second'] if 'second' in alarm_json else 0
                days = alarm_json['days'] if 'days' in alarm_json else []
                alarm = Alarm(name = name, hour = hour, minute = minute, second = second, days = days)
                scheduler.add_alarm(alarm)
    return scheduler

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

    def __init__(self, hour, minute = 0, second = 0, days = [], name = ''):
        '''
        hour: hour on which to run the alarm
        minute: minute on which to run the alarm
        '''
        self.name = name
        self.hour = hour
        self.minute = minute
        self.second = second
        self.days = days

# FIXME: remove
def foo():
        print("working")
