#!/usr/bin/env python3
import os, datetime, json, gzip

def getdata():
    logfile = os.path.join(os.getenv('HOME', '.'), '.dap/appmon.log')
    print('logfile', logfile)

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
        yield t, [act, apps]

HOUR = 60 * 60  # seconds
DAY  = 24 * HOUR
WEEK = DAY * 7

stream = getdata()
f = None
month = None
for t, data in stream:
    t_month = datetime.date.fromtimestamp(t).strftime('%Y-%m')
    if t_month != month:
        month = t_month
        if f is not None:
            f.close()
        #f = gzip.open('dab-' + t_month + '.log.gz', 'wt')
        f = open('/home/martin/sleeplogger/cache/dab-' + t_month + '.log', 'w')
    f.write('%d %s\n' % (t, json.dumps(data)))
