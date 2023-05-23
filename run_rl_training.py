import io
import os
import subprocess
import time
from os import listdir, path, mkdir

root = 'experiments'

dirs = listdir(root)

for d in dirs:
    lock_loc = path.join(root, d, 'lock.txt')
    if not path.exists(lock_loc):
        print(d)
        with io.open(lock_loc, 'w') as f:
            f.write(str(time.time()))
        log = path.join(root, d, 'log.txt')
        with io.open(log, 'w') as f:
            subprocess.call(['python3', 'rl_train.py', path.join(root, d, 'config.json')],
                            stdout=f)
        with io.open(path.join(root, d, 'done.txt'), 'w') as f:
            f.write(str(time.time()))

print('No more experiments to run.')
