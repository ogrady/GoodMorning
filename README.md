# GoodMorning
Waking up to sunrise and random sounds of nature or explosions.

Moving to the city has it advantages and disadvantages.
For one the noise is horrible and passing cars will constantly point their spotlights through your window, forcing you to let the blinds down all the way.
Which I can't stand since I need a bit of light when I wake up to get out of bed properly.

Being the outdoorsman I am, I present to you *GoodMorning* - the poor man's ambient wakeup!

It basically does a colour transition on an LED strip over time and plays some ambient music and nature sounds.
The idea is not new but I hate that all apps I have tried so far use the same sounds every morning.
So here you go. Random, extendible sounds.

The app is still in early development and actually more for my personal use. 
But feel free to use and modify.

## Components
GoodMorning currently consists of several main components:

1. *display:* classes to give some visual output, especially colour transistions.
The intended use is with a WS2801 strip.

2. *audio:* a mixer which feeds random sounds from directories into an arbitrary (but not infinite...) number of audio channels
and with that creates a somewhat "natural" audio experience.

3. *alarm:* a scheduler which reads alarm times from a JSON file and starts an action at that time.

4. *goodmorning:* the main components which puts all of the above together:
at the scheduled times the colour transistion will start and audio will start playing.

### Audio
The audio mixer expects sounds in `.ogg` format. At least two channels are being used:
one for playing ambient sounds, one more for playing bird sounds. Three-ish more channels
can be added for ambient sounds (definite count has yet to be determined).
Sounds are selected and played randomly.

### Alarm
#### alarms.json
The app expects a file `alarms.json` to be located in the main directory of the app.
The expected format is:

```
  sceneries: {
    name: { , (string: name of the scenery, must be unique, can be referenced in the alarms sections)
        files: [..] ([string]: paths to read files from. See (1) below! 
    }
  },
  alarms: { (array of the following)
    name: .., (string: description OPTIONAL)
    hour: .., (int: hour at which to ring)
    minute: .., (int: minute at which to ring, OPTIONAL default 0)
    second: .., (int: second at which to ring, OPTIONAL default 0)
    days: [..], ([string]: 'mon',..,'sun', OPTIONAL default []. results in ringing every day)
    scenery: .., (string: any name of a scenery defined above)
    active: .., (boolean: whether to ring, OPTIONAL defaults to true)
    duration .., (int: seconds after which the alarm turns itself off automatically, OPTIONAL defaults to -1, which means just keep ringing)
  },
  lullabies: { (array of the following)
    name: .., (string: description, must be unique!)
    scenery: .., (string: any name of a scenery defined above)
    duration: .., (int: seconds after which the scenery turns itself off automatically, OPTIONAL defaults to -1, which means just keep ringing)
  }
```

(1): Each entry in this array is the input for one audio channel.
They can be arrays themselves. The entries can either be paths to
sound files or directories. Giving directories will walk them recursively
and draw all files from them again.
This section should therefore contain as many sections as audio channels
and at least two. The first section will always be the ambient channel.
All others will be sound effects.
Everything else is undefined behaviour. See this commented example:

```
    "sceneries":
    {
        "scene1":
        {
            "files": [
                "dir1/", # chan1: all files in dir1/
                "rain.ogg", # chan2: just rain.ogg
                ["dir2/", "rain.ogg"] # chan3: all files in dir2/ plus rain.ogg
                "rgb_deltas": [7,2,2], # RGB will be increased by (7,2,2) on each tick
                "rgb_max": [255,220,220], # RGB will be raised to no more than (255,220,220)
                "sleep": 0.5  # RGB will be updated after this many seconds
        }
    },
```

## Running the App
Run the app with `python goodmorning.py`. The main method accepts (expects!) two parameters:

1. `-d`: display type. Accepts `led` (LED strip), `pled` (pygame prototype), `sun` (sunrise in game window)
2. `-a`: audio mixer. Accepts `mix` (regular mixer as descibed above), `mute` (no audio)

Make sure that all files and directories as mentioned in this readme are present and accessible!
