#!/usr/bin/python
import argparse
import os
import sys
import time
import traceback
from os import system

import Utilities
import ipxe_server
from Automation import Automation
from FileLoader import FileLoader
from Logger.Logger import Logger
from ScriptFactory import ScriptFactory
from constant import *
from interactive import InteractiveShell

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
    # Dump default values into SCG Profile.
    logger = Logger().get_logger()
    scg_profile = dict((k, v[0]) for (k, v) in scg_default_values.items())

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
    parser.add_argument('-m', '--memory', help='How much memory assigned to VM', default=default_kvm_memory_allocated,
                        dest='memory', type=int)
    parser.add_argument('--private', help='Private Build', action='store_true')
    parser.add_argument('--kernel_path', help='Private build kernel location', dest='kernel_path', default='')
    parser.add_argument('--image_path', help='Private build image location', dest='image_path', default='')

    args = parser.parse_args(argv)

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

    scg_profile.update(vars(args))

    # Print current argument setting :
    logger.debug('VM Name : %s' % args.name)
    logger.debug('Target Model : %s' % args.type)
    logger.debug('Target Branch : %s' % args.branch)
    logger.debug('Target Build : %s' % args.build)
    logger.debug('NIC Count : %s' % args.nic)
    logger.debug('Memory allocated : %d' % args.memory)

    # version = args.build

    # TODO: Need validate SCG Parameters here

    try:
        f = FileLoader()
        if args.private:
            f.execute_customized(scg_profile)
        else:
            f.execute_jenkins(scg_profile)

        # cmd = ScriptFactory.create(scg_profile, f.local_qcow2_path, f.local_img_path,
        #                           f.local_kernel_path).generate()
        cmd = ScriptFactory.create(scg_profile, f.local_storage_params()).generate()
        logger.debug('executing command : %s' % cmd)

        if args.type != 'vscg':
            ipxe_server.create_ipxe_thread()

        system(cmd)

        if args.stage1_only:
            logger.debug('-1 or --stage1_only is set, installation completed.')
            logger.debug('Please setup SCG manually')

            if args.type == 'scg' or args.type == 'scge':
                # countdown 60 sec for closing IPXE
                logger.debug('Wait 60 sec for iPXE down...')
                time.sleep(60)
        else:
            # Auto install process
            Automation(scg_profile).execute()

    except Exception as e:
        logger.debug(e.message)
        traceback.print_exc()
    finally:
        logger.debug('Cleanup for ipxe server....')
        ipxe_server.cleanup_ipxe_thread()


if __name__ == '__main__':
    deploy(sys.argv[1:])
