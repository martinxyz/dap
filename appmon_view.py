#!/usr/bin/env python
from __future__ import division
from pylab import *
import os, time

HOUR = 60*60 # seconds
DAY  = 24*HOUR
TICK = 300 # seconds

ticks = 0
ticks_act = 0
t_start = None
appcount = {}
appcorr = {}

ignore_before_t = time.time() - 8*HOUR
ignore_before_t = 0

logfile = os.path.join(os.getenv('HOME', '.'), '.dap/appmon.log')
for line in open(logfile):
    if line.startswith('#'):
        continue
    line = line.strip()
    if not line:
        continue
    t, act, apps = line.split(None, 2)
    t = int(t)
    act = act == '1'
    apps = list(set(eval(apps)))

    if t < ignore_before_t:
        continue

    ticks += 1
    if not t_start:
        t_start = t
    if act:
        ticks_act += 1
        for name in apps:
            appcount[name] = appcount.get(name, 0) + 1
        apps.sort()
        for i in apps:
            for j in [s for s in apps if s > i]:
                appcorr[(i,j)] = appcorr.get((i,j), 0) + 1
t_end = t

print ticks, 'ticks recorded'
print '%d%% active' % (100*ticks_act/ticks)
print 'log spans %.1f days' % ((t_end - t_start)/DAY)
dur = ticks * TICK
dur_act = ticks_act * TICK
print 'average uptime %.1f hours per day, of which %.1f hours have activity' % (dur/(t_end-t_start)*24, dur_act/(t_end-t_start)*24)

apps = appcount.items()
apps.sort(key=lambda(x): x[1])
print 'If application use overlaps within 5mins, activity is counted for both:'
for name, count in apps[-10:]:
    print '% 5.1f hours: %s' % (count*TICK/HOUR, name)


corr = appcorr.items()
corr.sort(key=lambda(x): x[1])
print 'Most frequent co-appearance:'
for (name1, name2), count in corr[-10:]:
    print '% 5.1f hours: %s and %s' % (count*TICK/HOUR, name1, name2)
    
