#!/bin/bash
cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"
/usr/bin/python3 $SCRIPT_DIR/midi_magic_box.py > $SCRIPT_DIR/midi_magic_box.log 2>&1
