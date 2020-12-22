
#!/bin/bash

set +v

mytitle="Build Results"

# Require ASNI Escape Code support

python3 ./measure.py start

echo -e 'k'$mytitle'\'

echo ===================================================

python3 /Users/Andy/Documents/python_projects/PyPlusSource/pyplus.pyw

echo Program Finished With Exit Code $?

python3 ./measure.py stop

echo ===================================================

echo Exit in 10 secs...

sleep 10s
