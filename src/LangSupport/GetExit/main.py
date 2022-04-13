import subprocess
import time
import sys

argv = sys.argv[1:]

if argv:
    command = " ".join(argv)
else:
    sys.stderr.write("Error, please specify a command\n")
    sys.exit(1)

start = time.time()
process = subprocess.call(command, shell=True)
end = time.time()

exit_code = int(process)
time_taken = end - start
time_taken = round(time_taken, 3)

message = f"Process finished in {time_taken} seconds\n" \
          f"Exit code {exit_code}"

print(message)
