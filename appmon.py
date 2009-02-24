#!/usr/bin/env python
import subprocess
import os, sys
import time
import select

xrecord_child = subprocess.Popen('x11/activity_monitor', stdout=subprocess.PIPE)
focus_child = subprocess.Popen('x11/getfocuswindow', stdout=subprocess.PIPE)

slotduration = 5*60.0 # seconds
#slotduration = 3
lastslot = time.time()

slot_applications = []
slot_activity = False

children_stdouts = [xrecord_child.stdout, focus_child.stdout]

print >>sys.stderr, 'start at', int(time.time())
print '# new log starts, slot duration is', slotduration, 'seconds'
print '#', 'seconds', 'keyboard/mouse activity', 'applications with keyboard focus'
sys.stdout.flush()
while True:
    assert xrecord_child.poll() is None, 'xrecord child dead' 
    assert focus_child.poll() is None, 'focus child dead' 
    ready, trash1, trash2 = select.select(children_stdouts , [], [], 1.0)
    t = time.time()
    while t > lastslot + slotduration:
        # finish the last slot first
        print int(time.time()), int(slot_activity), list(set(slot_applications))
        sys.stdout.flush()
        if slot_applications:
            slot_applications = [slot_applications[-1]]
        slot_activity = False
        lastslot += slotduration
    for f in ready:
        data = os.read(f.fileno(), 1024)
        if f is xrecord_child.stdout:
            slot_activity = True
        elif f is focus_child.stdout:
            slot_applications.append(data.strip())
