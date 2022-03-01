#!/bin/bash
set +v
cd "/home/andy/Documents/Python/PyPlus/src/empty/.PyPlus/Tests"
python3 /home/andy/Documents/Python/PyPlus/src/measure.py start
printf "================================================
"
python3 "/home/andy/Documents/Python/PyPlus/src/empty/.PyPlus/Tests/test.py"
printf "================================================
"
echo Program Finished With Exit Code $?
python3 /home/andy/Documents/Python/PyPlus/src/measure.py stop
echo Press enter to continue...
read -rs  # This will pause the script
rm timertemp.txt
