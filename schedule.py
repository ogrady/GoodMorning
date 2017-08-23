import schedule
import time 
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

    def __init__(self, sleep = 60):
        # sleep: interval in seconds in which the Scheduler checks for pending jobs
        Thread.__init__(self, target = self.run)
        self._scheduler = schedule.Scheduler()
        self.running = False

    def stop(self):
        self.running = False

    def add_alarm(self, alarm):
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
        if not (0 <= value < 24):
            raise AlarmException("Invalid hour: %d" % (value,))
        self._hour = value

    @property
    def minute(self):
        return self._minute

    def ring(self):
        '''
        Action to take when this alarm rings.
        '''
        pass

    @minute.setter
    def minute(self, value):
        if not (0 <= value < 60):
            raise AlarmException("Invalid minutes: %d" % (value,))
        self._minute = value

    def __init__(self, hour, minute):
        '''
        hour: hour on which to run the alarm
        minute: minute on which to run the alarm
        '''
        self.hour = hour
        self.minute = minute

# FIXME: remove
def foo():
        print("working")