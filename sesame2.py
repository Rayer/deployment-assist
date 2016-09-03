#!/usr/bin/python

import sys

from Utils import Utilities

__author__ = 'rayer'


def print_usage():
    print('Usage : sesame2 <Serial Number>')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print_usage()
        exit(1)
    print(Utilities.get_sesame2(sys.argv[1]))
    exit(0)