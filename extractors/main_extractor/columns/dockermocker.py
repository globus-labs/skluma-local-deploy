import subprocess
import sys
import time

#TODO: 1. Create table that says whether extractor is running.
#TODO: 2. Get scaling factor.  This should be equivalent to number of rows that can be 'running' at once.
#TODO: 3. Query database -- if running extractors < scaling factor, pop queue.
#TODO: 4. After queue is popped call a new subprocess containing next file argument.

i = 0

#Okay so this leave this at 'while true'.
while i<1 :



    t0 = time.time()
    p = subprocess.Popen([sys.executable, 'ex_columns.py'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
    t1 = time.time()
    print (t1-t0)

    i += 1
