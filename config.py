'''
Loads config files.

version: 1.0
author: Daniel O'Grady  
'''
import json
import os
import util
import configparser
from alarm import Scheduler, SceneryAlarm, SceneryLullaby, Scenery

def read_alarms(file, scheduler = None):
    '''
    file: json file from which to read the alarms.
    See README.md for expected format.
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
                duration = alarm_json['duration'] if 'duration' in alarm_json else -1
                name = alarm_json['name'] if 'name' in alarm_json else ''
                hour = alarm_json['hour'] # mandatory!
                minute = alarm_json['minute'] if 'minute' in alarm_json else 0
                second = alarm_json['second'] if 'second' in alarm_json else 0
                days = alarm_json['days'] if 'days' in alarm_json else []
                scenery_key = alarm_json['scenery'] if 'scenery' in alarm_json else 'UNDEFINED'
                if not scenery_key in sceneries:
                    raise util.AlarmException("Invalid scenery key: '%s' for alarm '%s'" % (scenery_key, name))
                scenery = sceneries[scenery_key]
                alarm = SceneryAlarm(name = name, hour = hour, minute = minute, second = second, days = days, scenery = scenery, duration = duration)
                scheduler.add_alarm(alarm)
    return scheduler

def read_sceneries(file):
    '''
    file: json file from which to read the sceneries.
    See README.md for expected format.
    
    returns: a dictionary of (name -> Scenery)
    '''
    sceneries = {}
    with open(file) as fd:
        data = json.load(fd)
        for name, scenery_json in data['sceneries'].items():
            rd,gd,bd = scenery_json['rgb_deltas']
            rmax,gmax,bmax = scenery_json['rgb_max']
            sleep = scenery_json['sleep']
            channels = []
            files = scenery_json['files']
            for group in files:
                sound_files = []
                if not isinstance(group, list):
                    group = [group]
                for f in group:
                    if os.path.isdir(f):
                        files = list(os.walk(f))[0]
                        sound_files.extend(map(lambda s: "".join((files[0], s)), files[2])) # 0: root, 1: subdirs, 2: files
                    else:
                        sound_files.append(f)
                channels.append(sound_files)
            if name in sceneries:
                raise util.AlarmException("Duplicate name for scenery: '%s'. Name must be unique" % (name,))
            sceneries[name] = Scenery(name, channels, rd,gd,bd, rmax,gmax,bmax, sleep)
    return sceneries
    
def read_lullabies(file):
    '''
    file: json file from which to read the sceneries.
    See README.md for expected format.
    
    returns: a dictionary of (name -> Lullaby)
    '''
    lullabies = {}
    sceneries = read_sceneries(file)
    with open(file) as fd:
        data = json.load(fd)
        for name, lullaby_json in data['lullabies'].items():
            # FIXME: typecheck!
            if ' ' in name:
                raise util.AlarmException("Lullaby name may not contain spaces ('%s')" % name) # must be identifiable by CommandDispatcher
            if not name or name == '' or name in lullabies:
                raise util.AlarmException("Lullabies must have a unique name. Invalid or duplicate name: '%s'" % name)
            scenery_key = lullaby_json['scenery'] if 'scenery' in lullaby_json else 'UNDEFINED'
            if not scenery_key in sceneries:
                raise util.AlarmException("Invalid scenery key: '%s' for lullaby '%s'" % (scenery_key, name))
            scenery = sceneries[scenery_key]
            duration = lullaby_json['duration'] if 'duration' in lullaby_json else -1
            lullaby = SceneryLullaby(name = name, scenery = scenery, duration = duration)
            lullabies[name] = lullaby
    return lullabies

def read_config_value(file, section, key, default = None):
    '''
    Reads a config entry from the passed position.
    Note that this is a rather expensive function (IO)
    and shouldn't be used excessively!
    
    file: cfg file to read from
    section: [SECTION] to read from
    key: the key under which to find the entry in the section
    default: the default value. If the default is None (default case!)
             this will raise an exception!
    
    returns: either the found value or None if either the
             section or the key were not found inside the file
    '''
    config = configparser.ConfigParser()
    value = default
    with open(file) as fp:
        config.readfp(fp)
        try:
            value = config.get(section, key)
        except (configparser.NoSectionError, KeyError, configparser.NoOptionError):
            if default is None:
                raise util.ConfigException("Couldn't find value for key '%s' in section '%s' of file '%s'" % (key, section, file))
            else:
                value = default
    return value
