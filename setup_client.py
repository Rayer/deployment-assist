import os

import sys


def setup_main():
    os.system('python get-pip.py')
    os.system('pip install -r requirements.txt')
    os.system('python vmmanage.py syslink')


if __name__ == '__main__':
    euid = os.geteuid()
    if euid != 0:
        print "Script not started as root. Running sudo.."
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        # the next line replaces the currently-running process with the sudo
        os.execlpe('sudo', *args)

    setup_main()
