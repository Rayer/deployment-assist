#!/usr/bin/python
import argparse
import re

from Comm.Broadcaster import Broadcaster
from Comm.Cmds import *
import Comm.CommConfig
__author__ = 'rayer'


class CmdHandler:
    def __init__(self):
        self.broadcaster = Broadcaster(Comm.CommConfig.proto_port)

    def discovery(self, vm_detail=False, host_ip=None):
        server_info_list = self.broadcaster.broadcast(GetVMList())
        for server_info in server_info_list:
            if not vm_detail:
                print('KVM : %s\tOnline:%d\tOffline:%d' % (server_info[1][0], server_info[0]['running'].__len__(), server_info[0]['shutdown'].__len__()))
                continue
            # prepare detail
            print('KVM IP : %s' % server_info[1][0])
            print('Running VMs Count : %d' % server_info[0]['running'].__len__())
            for running in server_info[0]['running']:
                print('[%3s]\t\t%s' % (running['id'], running['name']))
            print('Shut VMs Count : %d' % server_info[0]['shutdown'].__len__())
            for name in server_info[0]['shutdown']:
                print('[---]\t\t%s' % name)

            print('')

    def stats(self):
        print(self.broadcaster.broadcast(GetKVMHostStat()))

    def deploy(self, vm_name, host_ip=None):
        pass

    def delete(self, vm_name, host_ip=None):
        pass

    def sesame2(self, serial):
        sesame2_list = self.broadcaster.broadcast(RequestSesame2(serial))
        print(sesame2_list)

    def reconfig_vm(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KVM Deployment Assist Cluster Tools')
    sub_parsers = parser.add_subparsers(help='Sub-command help', dest='subcmd')

    discovery_parser = sub_parsers.add_parser('discovery', help='Discovery commands')
    discovery_parser.add_argument('-v', '--verbose', help='List detailed KVM Guest info', action='store_true')

    # Deploy action, now only supports interactive
    deploy_parser = sub_parsers.add_parser('stats', help='Get Host status')

    # Deploy action, now only supports interactive
    deploy_parser = sub_parsers.add_parser('deploy', help='Deploy a VM')
    deploy_parser.add_argument('name', help='VM Name')

    delete_parser = sub_parsers.add_parser('delete', help='Delete a VM')
    delete_parser.add_argument('name', help='VM Name')

    sesame2_parser = sub_parsers.add_parser('sesame2', help='Get Sesame2')
    sesame2_parser = sesame2_parser.add_argument('serial', help='Ask serial')

    parser.add_argument('-t', '--target', metavar='Target Address', help='Specify target server', dest='ip')

    args = parser.parse_args()

    if args.ip:
        # do IP validation
        ip_pattern = \
            re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        if not ip_pattern.match(args.ip):
            raise ValueError('IP address %s seems not a valid IP address!' % args.ip)

    if args.subcmd == 'discovery':
        CmdHandler().discovery(args.verbose, args.ip)

    if args.subcmd == 'stats':
        CmdHandler().stats()

    if args.subcmd == 'deploy':
        CmdHandler().deploy(args.name, args.ip)

    if args.subcmd == 'delete':
        CmdHandler().delete(args.name, args.ip)

    if args.subcmd == 'sesame2':
        CmdHandler().sesame2(args.serial)

