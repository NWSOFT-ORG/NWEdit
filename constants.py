"""Constants for the editor."""
from modules import *

WINDOWS = bool(sys.platform.startswith('win'))
OSX = bool(sys.platform.startswith('darwin'))
APPDIR = Path(__file__).parent
VERSION = '5.0'
os.chdir(APPDIR)
ICON = (
    'iVBORw0KGgoAAAANSUhEU\n'
    'gAAACAAAAAgBAMAAACBVGfHAAAAAXNSR0IB2cksfwAAAAlwSFlzAAASdAAAEnQB3mYfeAAA\n '
    'ABJQTFRFAAAAAAAA////TWyK////////WaqEwgAAAAZ0Uk5TAP8U/yr/h0gXnQAAAHpJREF\n '
    'UeJyNktENgCAMROsGog7ACqbpvzs07L+KFCKWFg0XQtLHFQIHAEBoiiAK2BSkXlBpzWDX4D\n '
    'QGsRhw9B3SMwNSSj1glNEDqhUpUGw/gMuUd+d2Csny6xgAZB4A1IDwG1SxAc/95t7DAPPIm\n '
    '4/BBeWjdGHr73AB3CCCXSvLODzvAAAAAElFTkSuQmCC')
BATCH_BUILD = ('''#!/bin/bash
set +v
cd "{script_dir}"
python3 {dir}/measure.py start
printf "================================================\n"
{cmd} "{file}"
printf "================================================\n"
echo Program Finished With Exit Code $?
python3 {dir}/measure.py stop
echo Press enter to continue...
read -s  # This will pause the script
rm timertemp.txt
''' if not WINDOWS else '''@echo off
title Build Results
cd "{script_dir}"
{dir}/measure.py start
echo.
echo.
echo ----------------------------------------------------
{cmd} "{file}"
echo Program Finished With Exit Code %ERRORLEVEL%
{dir}/measure.py stop
echo ----------------------------------------------------
echo.
del timertemp.txt
pause
''')  # The batch files for building.
LINT_BATCH = ('''#!/bin/bash
{cmd} "$1" > results.txt
exit
''' if not WINDOWS else '''@echo off
{cmd} "%1" > results.txt
exit''')
MAIN_KEY = 'Command' if OSX else 'Control'  # MacOS uses Cmd, but others uses Ctrl
_TK_VERSION = int(float(tk.TkVersion) * 10)  # Gets tkinter's version
BLOCK_WIDTH = 16
BLOCK_HEIGHT = 32
BLOCK_SIZE = BLOCK_WIDTH * BLOCK_HEIGHT
ENCODINGS = ("ASCII", "CP037", "CP850", "CP1140", "CP1252", "Latin1",
             "ISO8859_15", "Mac_Roman", "UTF-8", "UTF-8-sig", "UTF-16",
             "UTF-32")
textchars = bytearray({7, 8, 9, 10, 12, 13, 27}
                      | set(range(0x20, 0x100)) - {0x7f})
