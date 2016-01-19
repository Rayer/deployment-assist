#!/usr/bin/python
from Utilities import pid_lock_utils

from Comm.Responser import responser_main

__author__ = 'rayer'

if __name__ == '__main__':
    pid_lock_utils('/tmp/server.pid', responser_main)

