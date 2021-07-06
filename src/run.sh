#!/bin/bash
set +v
cd "/home/runner/PyPlus/src"
python3 /home/runner/PyPlus/src/measure.py start
printf "================================================
"
python3 "/home/runner/PyPlus/src/console.py"
printf "================================================
"
echo Program Finished With Exit Code $?
python3 /home/runner/PyPlus/src/measure.py stop
echo Press enter to continue...
read -rs  # This will pause the script
rm timertemp.txt
