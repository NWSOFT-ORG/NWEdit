"""Constants for the editor."""
from modules import *

WINDOWS = bool(sys.platform.startswith('win'))
OSX = bool(sys.platform.startswith('darwin'))
APPDIR = str(Path(__file__).parent)
VERSION = '6.0'
RUN_BATCH = ('''#!/bin/bash
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
TK_VERSION = int(float(tk.TkVersion) * 10)  # Gets tkinter's version
BLOCK_WIDTH = 16
BLOCK_HEIGHT = 32
BLOCK_SIZE = BLOCK_WIDTH * BLOCK_HEIGHT
ENCODINGS = ('ascii',
             'big5',
             'big5hkscs',
             'cp037',
             'cp273',
             'cp424',
             'cp437',
             'cp500',
             'cp720',
             'cp737',
             'cp775',
             'cp850',
             'cp852',
             'cp855',
             'cp856',
             'cp857',
             'cp858',
             'cp860',
             'cp861',
             'cp862',
             'cp863',
             'cp864',
             'cp865',
             'cp866',
             'cp869',
             'cp874',
             'cp875',
             'cp932',
             'cp949',
             'cp950',
             'cp1006',
             'cp1026',
             'cp1125',
             'cp1140',
             'cp1250',
             'cp1251',
             'cp1252',
             'cp1253',
             'cp1254',
             'cp1255',
             'cp1256',
             'cp1257',
             'cp1258',
             'cp65001',
             'euc_jp',
             'euc_jis_2004',
             'euc_jisx0213',
             'euc_kr',
             'gb2312',
             'gbk',
             'gb18030',
             'hz',
             'iso2022_jp',
             'iso2022_jp_1',
             'iso2022_jp_2',
             'iso2022_jp_2004',
             'iso2022_jp_3',
             'iso2022_jp_ext',
             'iso2022_kr',
             'latin_1',
             'iso8859_2',
             'iso8859_3',
             'iso8859_4',
             'iso8859_5',
             'iso8859_6',
             'iso8859_7',
             'iso8859_8',
             'iso8859_9',
             'iso8859_10',
             'iso8859_11',
             'iso8859_13',
             'iso8859_14',
             'iso8859_15',
             'iso8859_16',
             'johab',
             'koi8_r',
             'koi8_t',
             'koi8_u',
             'kz1048',
             'mac_cyrillic',
             'mac_greek',
             'mac_iceland',
             'mac_latin2',
             'mac_roman',
             'mac_turkish',
             'ptcp154',
             'shift_jis',
             'shift_jis_2004',
             'shift_jisx0213',
             'utf_32',
             'utf_32_be',
             'utf_32_le',
             'utf_16',
             'utf_16_be',
             'utf_16_le',
             'utf_7',
             'utf_8',
             'utf_8_sig')
textchars = bytearray({7, 8, 9, 10, 12, 13, 27}
                      | set(range(0x20, 0x100)) - {0x7f})
