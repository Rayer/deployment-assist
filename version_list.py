#!/usr/bin/python
import argparse
import sys

from Utils import Utilities

__author__ = 'rayer'


if __name__ == '__main__':
    supported_version = Utilities.get_supported_branches()
    parser = argparse.ArgumentParser(description='Branch version checker')
    parser.add_argument('branch', metavar='branch', choices=supported_version, \
                        help='Target Branch : %s ' % Utilities.get_supported_branches())
    parser.add_argument('type', metavar='type', choices=['scg', 'scge', 'vscg'], help='SCG Type : scg, vscg, scge')
    parser.add_argument('-F', '--full', help='Show full path', action='store_true')

    args = parser.parse_args()
    print ('Version Root : %s' % Utilities.get_branch_version_indicator(args.branch))
    print ('SCG Variant : %s' % args.type)

    if args.full:
        for path in Utilities.get_branch_download_dirs(args.branch, args.type):
            print(path)
    else:
        print ('Availible versions : ')
        for build in Utilities.get_branch_versions(args.branch, args.type):
            sys.stdout.write('%d ' % build)



