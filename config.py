'''
Loads config files.

version: 1.0
author: Daniel O'Grady  
'''
import json
import os
import util
from alarm import Scheduler, Alarm, Scenery

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
    sceneries = read_sceneries(file)
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
                scenery_key = alarm_json['scenery'] if 'scenery' in alarm_json else 'UNDEFINED'
                if not scenery_key in sceneries:
                    raise util.AlarmException("Invalid scenery key: '%s' for alarm '%s'" % (scenery_key, name))
                scenery = sceneries[scenery_key]
                alarm = Alarm(name = name, hour = hour, minute = minute, second = second, days = days, scenery = scenery)
                scheduler.add_alarm(alarm)
    return scheduler

def read_sceneries(file):
    '''
    file: json file from which to read the sceneries. They are expected
          to be in the format:
          sceneries: {
            name: ..: (description)
                files: [..] (array of files, see README.md)
          }
    '''
    sceneries = {}
    with open(file) as fd:
        data = json.load(fd)
        for name, scenery_json in data['sceneries'].items():
            channels = []
            files = scenery_json['files']
            for group in files:
                sound_files = []
                if not isinstance(group, list):
                    group = [group]
                for f in group:
                    if os.path.isdir(f):
                        sound_files.extend(list(os.walk(f))[0][2]) # 0: root, 1: subdirs, 2: files
                    else:
                        sound_files.append(f)
                channels.append(sound_files)
        sceneries[name] = Scenery(name, channels)
    return sceneries
