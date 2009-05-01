#!/usr/bin/env python
import os, time

clipboard = ''
while 1:
    new = os.popen('xsel -o').read()
    if clipboard != new:
        clipboard = new
        print clipboard
    time.sleep(0.1)
