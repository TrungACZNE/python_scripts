#!/usr/bin/python

import os
import time
import string
import sys

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
while True:
    line = sys.stdin.read(512)
    if line == "":
        break
    for c in line:
        sys.stdout.write(c)
        if c in string.letters:
            time.sleep(0.05)
