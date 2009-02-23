import os, time

class Process:
    pass

def proc2str(pid):
    try:
        return pid + ' ' + os.readlink('/proc/%s/exe' % pid) + ' ' + open('/proc/%s/cmdline' % pid).read().replace('\0', ' ').replace('\n', ' ')
    except:
        return '<unreadable>'

pids_old = set(os.listdir('/proc/'))
while True:
    pids_new = set(os.listdir('/proc/'))
    created    = pids_new.difference(pids_old)
    terminated = pids_old.difference(pids_new)
    pids_old = pids_new
    for pid in created:
        print proc2str(pid)
    for pid in terminated:
        pass
    time.sleep(0.050)
