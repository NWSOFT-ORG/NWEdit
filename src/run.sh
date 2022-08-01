#!/bin/bash
set +v
cd "/Users/andy/Documents/Projects/PyPlus"
python3 /Users/andy/Documents/Projects/PyPlus/src/measure.py start
printf "================================================
"
python3 "/Users/andy/Documents/Projects/PyPlus/main.py"
printf "================================================
"
echo Program Finished With Exit Code $?
python3 /Users/andy/Documents/Projects/PyPlus/src/measure.py stop
echo Press enter to continue...
read -rs  # This will pause the script
rm timertemp.txt
