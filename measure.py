import sys
import time

if sys.argv[1] == 'start':
	first = time.time()
	with open('timertemp.txt', 'w') as f:
		f.write(str(first))

elif sys.argv[1] == 'stop':
	with open('timertemp.txt') as f:
		first = "%.1f" % float(f.read())
	second = "%.1f" % time.time()
	print('Build taken {} seconds.'.format(round(float(second)-float(first), 2)))

