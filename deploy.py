#!/usr/bin/python
import argparse
import os
import socket
import sys
import time
import traceback
from os import system

from Automation import Automation
from FileLoader import FileLoader
from Logger.Logger import Logger
from ScriptFactory import ScriptFactory
from Utils import ipxe_server, Utilities
from Utils.APIOperation import APIOperation
from Utils.Email import *
from Utils.ProfileUtils import SCG_PROFILE
from Utils.database import open_scg_dao
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


def prepare_snapshot(ip):
    api = APIOperation(ip=ip)
    api.do_login()
    uuid = api.do_get_control_plane_list()['list'][0]['cpUUID']
    return api.do_get_snap_logs(uuid).content


def deploy(argv):
    # Dump default values into SCG Profile.
    logger = Logger().get_logger()
    scg_profile = SCG_PROFILE((k, v[0]) for (k, v) in scg_default_values.items())
    scg_profile.update({'init_time': time.mktime(time.localtime())})

    supported_version = Utilities.get_supported_branches()

    parser = argparse.ArgumentParser(description='SCG Deploy Utility. Current only supports scg/vscg')
    parser.add_argument('name', metavar='name')
    parser.add_argument('-t', '--type', choices=['scg', 'scge', 'vscg'], help='target SCG type', default='vscg',
                        dest='type')
    parser.add_argument('-b', '--branch', choices=supported_version, help='Target branch', default='ml', dest='branch')
    parser.add_argument('-B', '--build', help='Target Build Number', default='0', dest='build')
    # parser.add_argument('-n', '--nic', choices=[1, 3], help='NIC Count', type=int, default='3', dest='nic')
    parser.add_argument('-i', '--interactive', help='Interactive mode, all other argument will be ignored!',
                        action='store_true')
    parser.add_argument('-6', '--ipv6', help='Active IPV6', action='store_true')
    parser.add_argument('-1', '--stage1_only', help='Only download/install SCG, don\'t do automation setup',
                        action='store_true')
    parser.add_argument('-f', '--force', help='Delete conflict VMs on sight without prompt', action='store_true')
    parser.add_argument('-m', '--memory', help='How much memory assigned to VM', default=default_kvm_memory_allocated,
                        dest='memory', type=int)
    parser.add_argument('--private', help='Private Build', action='store_true')
    parser.add_argument('--kernel_path', help='Private build kernel location', dest='kernel_path', default='')
    parser.add_argument('--image_path', help='Private build image location', dest='image_path', default='')
    parser.add_argument('--sanity_test', help='Test sanity of a build', action='store_true')
    parser.add_argument('--email', help='Sanity test email inform target',
                        default='dl-tdc-eng-nms-scg-app@ruckuswireless.com')

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
    if args.build == '0':
        args.build = Utilities.get_most_recent_version(args.branch, args.type)

    if args.interactive:
        InteractiveShell(args).execute()
    elif args.private:
        # if build is 0, it means we should get most recent build
        pass

    if will_delete_old_vm:
        Utilities.del_vm(args.name)

    scg_profile.update(vars(args))

    # TODO: Need validate SCG Parameters here

    succeed = False
    try:
        scg_profile.update({'status': 'downloading'})
        f = FileLoader()
        if args.private:
            scg_profile.update({'branch': 'private', 'build': 'None'})
            f.execute_customized(scg_profile)
        else:
            f.execute_jenkins(scg_profile)

        cmd = ScriptFactory.create(scg_profile, f.local_storage_params()).generate()
        logger.debug('executing command : %s' % cmd)
        scg_profile.update({'status': 'stage1'})
        with open_scg_dao() as dao:
            dao.update(scg_profile)

        if args.type != 'vscg':
            ipxe_server.create_ipxe_thread()

        system(cmd)

        if args.stage1_only:
            logger.debug('-1 or --stage1_only is set, installation completed.')
            logger.debug('Please setup SCG manually')
            succeed = True
            scg_profile.update({'status': 'unmanaged'})
            with open_scg_dao() as dao:
                dao.update(scg_profile)
            if args.type == 'scg' or args.type == 'scge':
                # countdown 60 sec for closing IPXE
                logger.debug('Wait 60 sec for iPXE down...')
                time.sleep(60)

        else:
            # Auto install process
            scg_profile.update({'status': 'setup'})
            with open_scg_dao() as dao:
                dao.update(scg_profile)
            auto = Automation(scg_profile)
            auto.execute()
            succeed = True

    except Exception as e:
        logger.debug(e.message)
        traceback.print_exc()
        succeed = False
    finally:
        logger.debug('Cleanup for ipxe server....')
        ipxe_server.cleanup_ipxe_thread()
        scg_profile.update({'status': 'running' if succeed else 'damaged'})
        scg_profile.update_lastseen()
        with open_scg_dao() as dao:
            dao.update(scg_profile)

        if args.sanity_test:
            # Sanity test result
            print('Sanity Test result : %r' % succeed)
            sender = 'sanity-test@{}'.format(socket.gethostname())
            if succeed:
                logger.info(
                    'Sanity test for %s for profile %s is completed, deleting %s' % (args.name, args.type, args.name))
                send_email('Sanity Test Result %s@%s - %s' % (scg_profile['build'], scg_profile['branch'], 'Succeed'),
                           sender, [args.email], 'Setup succeed!')
                Utilities.del_vm(args.name)
                return True
            else:
                snapshot = None
                err = None
                if 'auto' in locals():
                    try:
                        ip = auto.ip_attr['Management']['IP Address']
                        snapshot = prepare_snapshot(ip)
                        print('Snapshot size : {}'.format(snapshot.__len__()))
                    except Exception as e:
                        print('Fail to get snapshot!')
                        err = e
                else:
                    logger.error('Fail to get IP, no snapshot is attached!')

                logger.info(
                    'Sanity test for %s for profile %s is completed, won\'t %s' % (args.name, args.type, args.name))
                send_email('Sanity Test Result %s@%s - %s' % (scg_profile['build'], scg_profile['branch'], 'Failed!'),
                           sender, [args.email],
                           '''
Setup Failed! please download snapshot manually

{}
                           '''.format(traceback.format_exc()))
                if snapshot is not None:
                    send_email(
                        'Sanity Test Result %s@%s - %s' % (scg_profile['build'], scg_profile['branch'], 'Failed!'),
                        sender, [args.email], 'Setup Failed!!',
                        snapshot)
                return False

    return succeed


if __name__ == '__main__':
    success = deploy(sys.argv[1:])
    exit(1 if success else 0)
