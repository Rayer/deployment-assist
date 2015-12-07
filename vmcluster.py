#!/usr/bin/python
import argparse
from Comm.Broadcaster import Broadcaster
from Comm.Cmds import *
import Comm.CommConfig
__author__ = 'rayer'


class CmdHandler:
    def __init__(self):
        self.broadcaster = Broadcaster(Comm.CommConfig.proto_port)

    def discovery(self, vm_detail=False):
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

            print('---------------------------')
            print('')

    def remote_vm(self, vm_identifier):
        pass

    def purge_vm(self, vm_identifier=None):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KVM Deployment Assist Cluster Tools')
    sub_parsers = parser.add_subparsers(help='Sub-command help', dest='subcmd')

    discovery_parser = sub_parsers.add_parser('discovery', help='Discovery commands')
    discovery_parser.add_argument('-v', '--verbose', help='List detailed KVM Guest info', action='store_true')
    args = parser.parse_args()

    if args.subcmd == 'discovery':
        CmdHandler().discovery(args.verbose)




