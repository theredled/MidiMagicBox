# MIDI Magic Box

Midi Magic Box is a Python software, mainly for Raspberry PI but compatible at least with MacOS and most Linux. 
Midi Magic Box provides ability to:
- Control velocity of MIDI keyboards
- Provides Presets system for said Yamaha Reface CP
- Provides secondary volume for Reface CP (useful for presets)
- All parameters are controlled via a separate channel (via a separate device such as Akai LPD8 for example)
- Linked to Samplerbox (https://github.com/theredled/SamplerBox) to provide sampling abilities.
- A plugin system to easily implement new features in Python

Install on RPi
----
- Linux modules : `libasound2-dev`, `python-dev`
- Python modules : `mido`, `python-rtmidi` (NOT `rtmidi-python`)
- `/home/pi$` `git clone https://github.com/theredled/MidiMagicBox`
- Make sure that `/home/pi/MidiMagicBox/startup.sh` is executable
- Append `su -c /home/pi/MidiMagicBox/startup.sh pi &` to `/etc/rc.local`
- Copy `src/config.py.sample` to `src/config.py`
- *(Optional)*  Modify `src/config.py` if you want to change MIDI channels (etc).
  
*+ SamplerBox :*
- Install forked Samplerbox : https://github.com/theredled/SamplerBox
- Append `export PYTHONPATH=$PYTHONPATH:/home/pi/SamplerBox` to `/etc/rc.local`

Documentation
----
- Specs MIDI Reface : https://jp.yamaha.com/files/download/other_assets/7/794817/reface_en_dl_b0.pdf
- Doc Mido : https://readthedocs.org/projects/mido/downloads/pdf/latest/
- Manuel Reface CS :  https://www.manualslib.com/manual/959024/Yamaha-Reface-Cs.html?page=47#manual
- Manuel Reface : https://aadl.org/files/catalog_guides/1508075_reface_manual.pdf

Option :
- https://www.yamahasynth.com/learn/reface/reface-cp-midi-primer-setting-midi-receive-channel

# About

Author : Benoît Guchet (twitter: [@Yoggghourt](https:/twitter.com/yoggghourt), mail: [benoit.guchet@gmail.com](mailto:benoit.guchet@gmail.com))
