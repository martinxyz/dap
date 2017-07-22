#!/usr/bin/env python3
import subprocess
import os, sys
import time, math
import select
import socket

# graphite
server_address = ('10.0.0.10', 2003)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(server_address)
def send2graphite(name, value, t):
    msg = 'bazaar.dap.timemon.%s %s %s\n' % (name, value, t)
    try:
        sock.sendall(msg.encode('ascii'))
    except socket.error:
        pass # happens when graphite is restarted

def time2str(t):
    if t < 2.2*60:
        return '%d seconds' % t
    elif t < 2.2*60*60:
        return '%d minutes' % (t/60)
    else:
        return '%d hours' % (t/60/60)

last_graphite_data = {}

xrecord_child = subprocess.Popen('x11/activity_monitor', stdout=subprocess.PIPE)
focus_child = subprocess.Popen('x11/getfocuswindow', stdout=subprocess.PIPE)

slotduration = 5 # seconds
lastslot = time.time()

slot_applications = []
slot_activity = False
slot_key_press = 0
slot_mouse_motion = 0
slot_mouse_click = 0

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
        browser_focus = b'Firefox' in slot_applications
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
                    #warntime = 5*60
                    #warntime = 14*60
                    warntime = 26*60
                if webtime > warntime:
                    #subprocess.call(['notify-send', '-u', 'critical', 'passing', time2str(warntime)])
                    subprocess.call(['notify-send', 'passing', time2str(warntime)])
                    #subprocess.call(['notify-send', '-u', 'critical', 'passing', time2str(warntime)])
                    #subprocess.call(['notify-send', '-u', 'critical', 'passing', time2str(warntime)])
                    warntime *= 2.5
        print('state', state, 'webtime', webtime, 'fac', fac)

        send2graphite('key_press', slot_key_press, lastslot)
        send2graphite('mouse_motion', slot_mouse_motion, lastslot)
        send2graphite('mouse_click', slot_mouse_click, lastslot)
        if slot_activity:
            send2graphite('activity', 1, lastslot)
        else:
            send2graphite('activity', 1, lastslot)
        send2graphite('state', state, lastslot)

        # finish the last slot first
        #print(int(time.time()), int(slot_activity), list(set(slot_applications)))
        sys.stdout.flush()
        if slot_applications:
            slot_applications = [slot_applications[-1]]
        slot_activity = False
        slot_key_press = 0
        slot_mouse_motion = 0
        slot_mouse_click = 0
        lastslot += slotduration

    for f in ready:
        data = os.read(f.fileno(), 1024)
        if f is xrecord_child.stdout:
            #print('xrecord:', repr(data))
            for line in data.split(b'\n'):
                if b'ButtonPress' in line:
                    slot_mouse_click += 1
                if b'Motion' in line:
                    slot_mouse_motion += 1
                if b'KeyPress' in line:
                    slot_key_press += 1
            slot_activity = True
        elif f is focus_child.stdout:
            #print('focus:', repr(data))
            slot_applications.append(data.strip())

