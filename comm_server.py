#!/usr/bin/python
from Comm.Responser import responser_main
from Utilities import pid_lock_utils

__author__ = 'rayer'

if __name__ == '__main__':
    pid_lock_utils('/var/run/comm_server.pid', responser_main)
