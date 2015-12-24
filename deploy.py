#!/usr/bin/python
import argparse
import os
from os import system

import Utilities
import ipxe_server
from Automation import Automation
from FileLoader import FileLoader
from ScriptFactory import ScriptFactory
from interactive import InteractiveShell
import time
import traceback
import sys

__author__ = 'rayer'


''' Use cases :
    deploy # deploy with "SCG, Mainline, newest"
    deploy scg_name --type vscg
    deploy scg_name --profile vscg-standard
    deploy scg_name --branch Mainline # Branch defination is in external file
    deploy scg_name --branch Mainline --build 720

    For branch mapping, it will be described in constant.py
'''


def deploy(argv):
    supported_version = Utilities.get_supported_branches()

    parser = argparse.ArgumentParser(description='SCG Deploy Utility. Current only supports scg/vscg')
    parser.add_argument('name', metavar='name')
    parser.add_argument('-t', '--type', choices=['scg', 'scge', 'vscg'], help='target SCG type', default='vscg', dest='type')
    parser.add_argument('-b', '--branch', choices=supported_version, help='Target branch', default='ml', dest='branch')
    parser.add_argument('-B', '--build', help='Target Build Number', default='710', dest='build')
    # parser.add_argument('-n', '--nic', choices=[1, 3], help='NIC Count', type=int, default='3', dest='nic')
    parser.add_argument('-i', '--interactive', help='Interactive mode, all other argument will be ignored!', action='store_true')
    parser.add_argument('-6', '--ipv6', help='Active IPV6', action='store_true')
    parser.add_argument('-1', '--stage1_only', help='Only download/install SCG, don\'t do automation setup', action='store_true')
    parser.add_argument('-f', '--force', help='Delete conflict VMs on sight without prompt', action='store_true')

    parser.add_argument('--private', help='Private Build', action='store_true')
    parser.add_argument('--kernel_path', help='Private build kernel location', dest='kernel_path', default='')
    parser.add_argument('--image_path', help='Private build image location', dest='image_path', default='')

    args = parser.parse_args(argv)

    # Check private build arguments
    # if args.private:
    #     if parser.kernel_path  or parser.image_path:
    #         raise BaseException('--image_path or --kernel_path can\'t be used without --private!')

    os.chdir('/tmp')

    # Check if file exist :
    will_delete_old_vm = False
    if Utilities.get_vm_status(args.name) is not None:
        if args.force:
            will_delete_old_vm = True
        else:
            while True:
                choice = raw_input(
                    'VM Name %s exists! Proceed will cause it being deleted, are your sure (y/N):' % args.name)
                if choice == 'n':
                    exit(0)
                elif choice == 'y':
                    will_delete_old_vm = True
                    break

    # args.nic = 1 if args.type == 'scge' else 3
    args.nic = 3
    # args.private = False
    if args.interactive:
        InteractiveShell(args).execute()
    elif args.private:
        # seems don't need to do anything....?
        pass

    if will_delete_old_vm:
        Utilities.del_vm(args.name)

    # Print current argument setting :
    print('VM Name : %s' % args.name)
    print('Target Model : %s' % args.type)
    print('Target Branch : %s' % args.branch)
    print('Target Build : %s' % args.build)
    print('NIC Count : %s' % args.nic)

    # version = args.build

    try:

        f = FileLoader()
        if args.private:
            f.execute_customized(args.type, args.name, args.image_path, args.kernel_path)
        else:
            f.execute_jenkins(args.type, args.name, args.branch, args.build)
        cmd = ScriptFactory.create(args.type, args.name, args.nic, f.qcow_path, f.scg_image_path, f.kernel_path).generate()
        print('executing command : %s' % cmd)

        if args.type != 'vscg':
            ipxe_server.create_ipxe_thread()

        system(cmd)

        if args.stage1_only:
            print('-1 or --stage1_only is set, installation completed.')
            print('Please setup SCG manually')

            if args.type == 'scg' or args.type == 'scge':
                # countdown 60 sec for closing IPXE
                print('Wait 60 sec for iPXE down...')
                time.sleep(60)
        else:
            # Auto install process
            Automation(args.type, args.name, args.ipv6).execute()

    except Exception as e:
        print(e.message)
        traceback.print_exc()
    finally:
        print('Cleanup for ipxe server....')
        ipxe_server.cleanup_ipxe_thread()


if __name__ == '__main__':
    deploy(sys.argv[1:])
