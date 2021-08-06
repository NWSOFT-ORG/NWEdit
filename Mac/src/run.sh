#!/bin/bash
set +v
cd "/home/runner"
python3 /home/runner/PyPlus/src/measure.py start
printf "================================================
"
bash "/home/runner/.bashrc"
printf "================================================
"
echo Program Finished With Exit Code $?
python3 /home/runner/PyPlus/src/measure.py stop
echo Press enter to continue...
read -rs  # This will pause the script
rm timertemp.txt
