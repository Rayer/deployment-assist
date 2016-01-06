#!/usr/bin/python
import os

from Comm.Responser import responser_main

__author__ = 'rayer'

if __name__ == '__main__':
    pid = str(os.getpid())
    pidfile = '/tmp/comm_server.pid'

    if os.path.isfile(pidfile):
        with open(pidfile, 'r') as file:
            old_pid = file.read(6)
        print('Service is already running at %s, deleting this and restart service' % old_pid)
        try:
            os.kill(int(old_pid), 9)
        except OSError as e:
            print('Seems there is some trouble deleting %s' % old_pid)
        finally:
            os.remove(pidfile)

    with open(pidfile, 'w') as file:
        print('Application starts as pid : %s' % pid)
        file.write(pid)

    try:
        responser_main()
    finally:
        os.remove(pidfile)
