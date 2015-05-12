PLC - Python Lighting Controls
=================================

A Python lighting board framework, using the Open Lighting Architecture
for USB-DMX interfacing. This repository contains the core server that
handles DMX output via OLA and cue playback, and can receive commands or
send status to several clients simultaneously.

Requirements
---------------------------------

- Python >= 3.4
- OLA with Python bindings (must be manually converted to Python 3)
  + and python3-protobuf

##### Python Packages
  - passlib


Cue Attributes
---------------------------------

- up
- down
- upwait
- downwait
- follow
- followtime
