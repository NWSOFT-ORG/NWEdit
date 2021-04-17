#!/bin/bash
set +v
cd "/Users/Andy/Documents/Projects/python_projects/PyPlus"
python3 /Users/Andy/Documents/Projects/python_projects/PyPlus/measure.py start
printf "================================================
"
python3 "/Users/Andy/Documents/Projects/python_projects/PyPlus/console.py"
printf "================================================
"
echo Program Finished With Exit Code $?
python3 /Users/Andy/Documents/Projects/python_projects/PyPlus/measure.py stop
echo Press enter to continue...
read -rs  # This will pause the script
rm timertemp.txt
