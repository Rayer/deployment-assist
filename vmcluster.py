#!/usr/bin/python
import argparse
import os
import re

import Comm.CommConfig
from Comm.Broadcaster import Broadcaster
from Comm.Cmds import *
from Utils.ProfileUtils import ProfileParser, smart_dict

__author__ = 'rayer'


class CmdHandler:
    def __init__(self):
        self.broadcaster = Broadcaster(Comm.CommConfig.proto_port)

    def show(self, vm_detail=False, host_ip=None):
        server_info_list = self.broadcaster.broadcast(GetVMList())
        for server_info in server_info_list:
            if not vm_detail:
                print('%s(%s)\tOnline:%d\tOffline:%d' % (
                    server_info[0].get('host', 'None'), server_info[1][0], server_info[0]['running'].__len__(),
                    server_info[0]['shutdown'].__len__()))
                continue
            # prepare detail
            print('KVM Name : %s' % server_info[0].get('host', 'None'))
            print('KVM IP : %s' % server_info[1][0])
            print('Running VMs Count : %d' % server_info[0]['running'].__len__())
            for running in server_info[0]['running']:
                p_parser = ProfileParser(running)
                running.update({'management_ip': p_parser.get_management_ip()})
                p_parser.get_status_color_print()(
                    '[%(id)s]:\t%(name)s\t%(management_ip)s\t%(type)s\t%(build)s@%(branch)s\t%(status)s' % smart_dict(running))

            print('Shut VMs Count : %d' % server_info[0]['shutdown'].__len__())
            for stopped in server_info[0]['shutdown']:
                p_parser = ProfileParser(stopped)
                stopped.update({'management_ip': None})
                p_parser.get_status_color_print()(
                    '[%(id)s]:\t%(name)s\t%(management_ip)s\t%(type)s\t%(build)s@%(branch)s\t%(status)s' % smart_dict(stopped))

            print('')

    def stats(self):
        stat = self.broadcaster.broadcast(GetKVMHostStat())
        index = 0
        for server_info in stat:
            server_info[0].update({'ip': server_info[1][0], 'index': index})
            index += 1
            print(
            '(%(index)d)\t%(ip)s(%(host)s)\tRunning:%(running)d\tShutdown:%(shutdown)d\tFree:%(free)s\tBuffer:%(buffers)s' %
            server_info[0])

    def deploy(self):
        stat = self.broadcaster.broadcast(GetKVMHostStat())
        index = 0
        for server_info in stat:
            server_info[0].update({'ip': self.__get_ip_from_server_info__(server_info), 'index': index})
            index += 1
            print(
            '(%(index)d)\t%(ip)s(%(host)s)\tRunning:%(running)d\tShutdown:%(shutdown)d\tFree:%(free)s\tBuffer:%(buffers)s' %
            server_info[0])
        server_index = int(raw_input('Select a VM : '))
        destination = stat[server_index]
        print('Will deploy to : %s(%s)' % (
        self.__get_ip_from_server_info__(destination), self.__get_host_from_server_info__(destination)))
        os.system('ssh -t root@%s -C \'vmmanage create\'' % self.__get_ip_from_server_info__(destination))


    def delete(self, vm_name, host_ip=None):
        pass

    def sesame2(self, serial):
        sesame2_list = self.broadcaster.broadcast(RequestSesame2(serial))
        print(sesame2_list)

    def reconfig_vm(self):
        pass

    def exec_cmd(self, cmd):
        res_list = self.broadcaster.broadcast(ExecCmd(cmd))
        for exec_res in res_list:
            print('From : %s(%s)' % (exec_res[0]['host'], exec_res[1][0]))
            print(exec_res[0]['res'])
            print('\n')

    def exec_search(self, vm_name_regex):
        ret = self.broadcaster.broadcast(GetVMList())
        pattern = re.compile(vm_name_regex)
        for server_info in ret:
            print('At %(ip)s(%(name)s) : ' % {'ip': self.__get_ip_from_server_info__(server_info),
                                              'name': self.__get_host_from_server_info__(server_info)})
            for running_vms in server_info[0]['running']:
                if pattern.match(running_vms['name']):
                    print('%s(%s)' % (running_vms['name'], 'Running'))

            for stop_vm in server_info[0]['shutdown']:
                if pattern.match(stop_vm['name']):
                    print('%s(%s)' % (stop_vm, 'Stopped'))
        print('\n\r')

    def exec_console(self):
        ret = self.broadcaster.broadcast(GetVMList())
        print('Available VMs : ')
        vm_list = []
        for server_info in ret:
            print('At %(ip)s(%(name)s) : ' % {'ip': server_info[1][0], 'name': server_info[0]['host']})
            for vm in server_info[0]['running']:
                vm_list.append((vm['name'], server_info[1][0]))
                print('(%d)(%s)' % (vm_list.__len__() - 1, vm['name']))

        select = int(raw_input('Select a VM : '))
        os.system('ssh -t root@%s -C \'virsh console %s\'' % (vm_list[select][1], vm_list[select][0]))

    @staticmethod
    def __get_ip_from_server_info__(server_info):
        return server_info[1][0]

    @staticmethod
    def __get_host_from_server_info__(server_info):
        return server_info[0]['host']


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='KVM Deployment Assist Cluster Tools')
    sub_parsers = parser.add_subparsers(help='Sub-command help', dest='subcmd')
    parser.add_argument('-d', '--debug', help='Enable console debugging', action='store_true')

    discovery_parser = sub_parsers.add_parser('show', help='Show commands')
    discovery_parser.add_argument('-v', '--verbose', help='List detailed KVM Guest info', action='store_true')

    stats_parser = sub_parsers.add_parser('stats', help='Get Host status')

    deploy_parser = sub_parsers.add_parser('deploy', help='Deploy a VM')
    # deploy_parser.add_argument('name', help='VM Name')

    delete_parser = sub_parsers.add_parser('delete', help='Delete a VM')
    delete_parser.add_argument('name', help='VM Name')

    sesame2_parser = sub_parsers.add_parser('sesame2', help='Get Sesame2')
    sesame2_parser.add_argument('serial', help='Ask serial')

    cmdexec_parser = sub_parsers.add_parser('exec', help='Execute a command for all hosts')
    cmdexec_parser.add_argument('command', help='(Danger)Command wants all client to execute')

    search_parser = sub_parsers.add_parser('search', help='Search VMs')
    search_parser.add_argument('keyword', help='Search keyword')

    console_parser = sub_parsers.add_parser('console', help='Connect to console')
    # console_parser.add_argument();

    parser.add_argument('-t', '--target', metavar='Target Address', help='Specify target server', dest='ip')

    args = parser.parse_args()

    if args.ip:
        # do IP validation
        ip_pattern = \
            re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        if not ip_pattern.match(args.ip):
            raise ValueError('IP address %s seems not a valid IP address!' % args.ip)

    if args.subcmd == 'show':
        CmdHandler().show(args.verbose, args.ip)

    if args.subcmd == 'stats':
        CmdHandler().stats()

    if args.subcmd == 'deploy':
        CmdHandler().deploy()

    if args.subcmd == 'delete':
        CmdHandler().delete(args.name, args.ip)

    if args.subcmd == 'sesame2':
        CmdHandler().sesame2(args.serial)

    if args.subcmd == 'exec':
        CmdHandler().exec_cmd(args.command)

    if args.subcmd == 'search':
        CmdHandler().exec_search(args.keyword)

    if args.subcmd == 'console':
        CmdHandler().exec_console()
