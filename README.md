# GoodMorning
Waking up to sunrise and random sounds of nature or explosions.

Moving to the city has it advantages and disadvantages.
For one the noise is horrible and passing cars will constantly point their spotlights through your window, forcing you to let the blinds down all the way.
Which I can't stand since I need a bit of light when I wake up to get out of bed properly.

Being the outdoorsman I am, I present to you *GoodMorning* - the poor man's ambient wakeup!

It basically ~runs a fullscreen app which~ does a colour transition over time and plays some ambient music and nature sounds.
The idea is not new but I hate that all apps I have tried so far use the same sounds every morning.
So here you go. Random, extendible sounds.

~You'd therefore have to have a monitor with speakers installed in your bedroom. But c'mon, it's 2017.~

The app is still in early development and actually more for my personal use. 
But feel free to use and modify.

## Components
GoodMorning currently consists of several main components:

1. *display:* several classes to give some visual output, especially colour transistions.
With my current setup I am using the LED display to control a WS2801 strip. But it also contains classes to control a display.

2. *audio:* a mixer which feeds random sounds from dictionaries into an arbitrary number of audio channels
and with that creates a somewhat "natural" audio experience.

3. *alarm:* a scheduler which reads alarm times from a JSON file and starts an action at that time.

4. *goodmorning:* the main components which puts all of the above together:
at the scheduled time the colour transistion will start and audio will start playing.

### Audio
The basic audio mixer expects two directories `ambient/` and `birds/` to be present in the main directory of the app.
Both are to contain sounds in `.ogg` format. Three channels are being used:
one for playing ambient sounds, two more for playing bird sounds.
Sounds are selected and played randomly.

### Alarm
#### alarms.json
The app expects a file `config.json` to be located in the main directory of the app.
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
  }
```

(1): Each entry in this array is the input for one audio channel.
They can be arrays themselves. The entries can either be paths to
sound files or directories. Giving directories will walk them recursively
and draw all files from them again.
This section should therefore contain as many sections as audio channels.
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
        }
    },
```

## Running the App
Run the app with `python goodmorning.py`. The main method accepts (expects!) two parameters:

1. `-d`: display type. Accepts `led` (LED strip), `pled` (pygame prototype), `sun` (sunrise in game window)
2. `-a`: audio mixer. Accepts `mix` (regular mixer as descibed above), `mute` (no audio)

Make sure that all files and directories as mentioned in this readme are present and accessible!
