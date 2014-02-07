#!/usr/bin/env python3
import subprocess
import os, sys
import time, math
import select

def time2str(t):
    if t < 2.2*60:
        return '%d seconds' % t
    elif t < 2.2*60*60:
        return '%d minutes' % (t/60)
    else:
        return '%d hours' % (t/60/60)

xrecord_child = subprocess.Popen('x11/activity_monitor', stdout=subprocess.PIPE)
focus_child = subprocess.Popen('x11/getfocuswindow', stdout=subprocess.PIPE)

slotduration = 5 # seconds
lastslot = time.time()

slot_applications = []
slot_activity = False

children_stdouts = [xrecord_child.stdout, focus_child.stdout]

print('start at', int(time.time()))
subprocess.call(['notify-send', 'Up and watching.'])
#print('# new log starts, slot duration is', slotduration, 'seconds')
#print('#', 'seconds', 'keyboard/mouse activity', 'applications with keyboard focus')
print('#', 'seconds', 'keyboard/mouse activity', 'applications with keyboard focus')
sys.stdout.flush()

state = 0.5
passiv_time = 0
webtime = 0
warntime = 0
while True:
    assert xrecord_child.poll() is None, 'xrecord child dead' 
    assert focus_child.poll() is None, 'focus child dead' 
    ready, trash1, trash2 = select.select(children_stdouts , [], [], 1.0)
    t = time.time()
    while t > lastslot + slotduration:
        browser_focus = b'Iceweasel' in slot_applications
        if slot_activity:
            passiv_time = 0
        else:
            passiv_time += slotduration
        fac = math.exp(-slotduration/(2*60))
        state *= fac
        if browser_focus:
            state += (1-fac) * math.exp(-passiv_time/(2*60))
            print('p-factor', math.exp(-passiv_time/(2*60)))
        print(slot_applications)
        if state < 0.1:
            webtime = 0
            warntime = 0
            print('reset')
        if state > 0.4:
            webtime += slotduration * math.exp(-passiv_time/(2*60))
            if slot_activity and browser_focus:
                if warntime == 0:
                    #warntime = 26.25
                    warntime = 5*60
                if webtime > warntime:
                    subprocess.call(['notify-send', 'passing', time2str(warntime)])
                    subprocess.call(['notify-send', 'passing', time2str(warntime)])
                    subprocess.call(['notify-send', 'passing', time2str(warntime)])
                    warntime *= 3
        print('state', state, 'webtime', webtime, 'fac', fac)

        # finish the last slot first
        #print(int(time.time()), int(slot_activity), list(set(slot_applications)))
        sys.stdout.flush()
        if slot_applications:
            slot_applications = [slot_applications[-1]]
        slot_activity = False
        lastslot += slotduration

    for f in ready:
        data = os.read(f.fileno(), 1024)
        if f is xrecord_child.stdout:
            #print('xrecord:', repr(data))
            slot_activity = True
        elif f is focus_child.stdout:
            #print('focus:', repr(data))
            slot_applications.append(data.strip())
