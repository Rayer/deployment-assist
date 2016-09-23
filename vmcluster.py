#!/usr/bin/python
import argparse
import os
import re

import Comm.CommConfig
from Comm.Broadcaster import Broadcaster
from Comm.Cmds import *
from Utils.ProfileUtils import ProfileParser, SCG_PROFILE

__author__ = 'rayer'


class CmdHandler:
    def __init__(self, broadcaster_ip_list=None):
        self.broadcaster = Broadcaster(Comm.CommConfig.proto_port, broadcaster_ip_list)

    def get_server_info_list(self):
        server_info_list = self.broadcaster.broadcast(GetVMList())
        server_info_list.sort()
        return server_info_list

    def show(self, vm_detail=False, host_ip=None):
        server_info_list = self.get_server_info_list()
        for server_info in server_info_list:
            if not vm_detail:
                print('%s(%s)\tOnline:%d\tOffline:%d' % (
                    server_info[0].get('host', 'None'), server_info[1][0], server_info[0]['running'].__len__(),
                    server_info[0]['shutdown'].__len__()))
                continue
            # prepare detail
            print('KVM Name : %s' % server_info[0].get('host', 'None'))
            print('KVM IP : {0}'.format(server_info[1][0]))
            print('Running VMs Count : %d' % server_info[0]['running'].__len__())
            for running in server_info[0]['running']:
                p_parser = ProfileParser(running)
                running.update({'management_ip': p_parser.get_management_ip(), 'control_ip': p_parser.get_control_ip()})
                p_parser.get_status_color_print()(
                    '[%(id)3s][%(status)-11s]:\t%(name)-30s\t%(type)5s\t%(build)5s@%(branch)-9s\t%(management_ip)-16s\t%(control_ip)-16s' % SCG_PROFILE(
                        running))

            print('Shut VMs Count : %d' % server_info[0]['shutdown'].__len__())
            for stopped in server_info[0]['shutdown']:
                p_parser = ProfileParser(stopped)
                stopped.update({'management_ip': None})
                p_parser.get_status_color_print()(
                    '[%(id)3s][%(status)-11s]:\t%(name)-30s\t%(type)5s\t%(build)5s@%(branch)-9s' % SCG_PROFILE(stopped))

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
        stat = sorted(stat, key=lambda k: k[0]['host'])
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

    def delete(self, name=None, host=None):
        ret_array = self.__exec_operation__('all', name, host)
        for (kvm_server, target_name) in ret_array:
            print('Deleting %s at %s...' % (target_name, kvm_server))
            os.system('ssh -t root@%s -C \'vmmanage delete %s\'' % (kvm_server, target_name))

    def exec_stop(self, name=None, host=None):
        ret_array = self.__exec_operation__('running', name, host)
        for (kvm_server, target_name) in ret_array:
            print('Stopping %s at %s...' % (target_name, kvm_server))
            os.system('ssh -t root@%s -C \'vmmanage stop %s\'' % (kvm_server, target_name))

    def exec_start(self, name=None, host=None):
        ret_array = self.__exec_operation__('shutdown', name, host)
        print('Starting %s in order... ' % ret_array.__str__())
        for (kvm_server, target_name) in ret_array:
            os.system('ssh -t root@%s -C \'vmmanage start %s\'' % (kvm_server, target_name))

    def exec_cmd(self, cmd, blocking):
        if blocking is True:
            target_list = self.get_server_info_list()
            print('Apply to below {} servers : '.format(len(target_list)))
            for vms in target_list:
                ip = vms[1][0]
                hostname = vms[0].get('host', 'None')
                print('===== {0}({1}) execution start ====='.format(hostname, ip))
                os.system('ssh -t root@%s -C \'%s\'' % (ip, cmd))
                print('===== {0}({1}) execution end =====\n'.format(hostname, ip))

        else:
            res_list = self.broadcaster.broadcast(ExecCmd(cmd))
            for exec_res in res_list:
                print('From : %s(%s)' % (exec_res[0]['host'], exec_res[1][0]))
                print(exec_res[0]['res'])
                print('\n')

    def exec_search(self, vm_name_regex):
        ret = self.get_server_info_list()
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

    def exec_console(self, name=None, host=None):
        ret_array = self.__exec_operation__('running', name, host)
        if ret_array.__len__() is not 1:
            print('Can\'t start multiple console at once!')
            exit(1)
        (kvm_server, target_name) = ret_array[0]
        os.system('ssh -t root@%s -C \'virsh console %s\'' % (kvm_server, target_name))

    def __exec_operation__(self, target_stat, name_filter=None, host_filter=None):
        name_pattern = re.compile(name_filter if name_filter is not None else '')
        host_pattern = re.compile(host_filter if host_filter is not None else '')
        ret = self.get_server_info_list()
        stat_list = ['running', 'shutdown'] if target_stat == 'all' else [target_stat]
        print('Available VMs : ')
        vm_list = []
        for server_info in ret:
            if not host_pattern.match(server_info[0]['host']):
                continue

            print('At %(ip)s(%(name)s) : ' % {'ip': server_info[1][0], 'name': server_info[0]['host']})
            for vm_stat in stat_list:
                for vm in server_info[0][vm_stat]:

                    if not name_pattern.match(vm['name']):
                        continue

                    pp = ProfileParser(vm)
                    vm_list.append((vm['name'], server_info[1][0]))
                    pp.get_status_color_print()(
                        '(%3d)[%-11s]\t%-30s' % (vm_list.__len__() - 1, pp.get_status(), vm['name']))
        select = raw_input('Select a VM : ')
        selection_array = select.split(' ')
        ret_array = []
        for selected in selection_array:
            ret_array.append((vm_list[int(selected)][1], vm_list[int(selected)][0]))
        # Return : 1. KVM Server, 2. Target SCG Name
        return ret_array

    @staticmethod
    def __get_ip_from_server_info__(server_info):
        return server_info[1][0]

    @staticmethod
    def __get_host_from_server_info__(server_info):
        return server_info[0]['host']


def add_filters(child_parser):
    child_parser.add_argument('--name', help='Add name filter')
    child_parser.add_argument('--host', help='Add host filter')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='KVM Deployment Assist Cluster Tools')
    sub_parsers = parser.add_subparsers(help='Sub-command help', dest='subcmd')
    parser.add_argument('-d', '--debug', help='Enable console debugging', action='store_true')
    parser.add_argument('-b', '--broadcast_addr', help='Broadcast Domain Address', dest='broadcast_addr')

    discovery_parser = sub_parsers.add_parser('show', help='Show commands')
    discovery_parser.add_argument('-v', '--verbose', help='List detailed KVM Guest info', action='store_true')

    stats_parser = sub_parsers.add_parser('stats', help='Get Host status')

    deploy_parser = sub_parsers.add_parser('deploy', help='Deploy a VM')

    delete_parser = sub_parsers.add_parser('delete', help='Delete a VM')
    add_filters(delete_parser)

    stop_parser = sub_parsers.add_parser('stop', help='Stop a SCG')
    add_filters(stop_parser)

    start_parser = sub_parsers.add_parser('start', help='Start a SCG')
    add_filters(start_parser)

    cmdexec_parser = sub_parsers.add_parser('exec', help='Execute a command for all hosts')
    cmdexec_parser.add_argument('-b', '--blocking', help='Block Mode, will execute one by one', action='store_true')
    cmdexec_parser.add_argument('command', help='(Danger)Command wants all client to execute')

    upgrade_parser = sub_parsers.add_parser('upgrade', help='Upgrade program for all hosts')

    search_parser = sub_parsers.add_parser('search', help='Search VMs')
    search_parser.add_argument('keyword', help='Search keyword')

    console_parser = sub_parsers.add_parser('console', help='Connect to console')
    add_filters(console_parser)

    parser.add_argument('-t', '--target', metavar='Target Address', help='Specify target server', dest='ip')

    args = parser.parse_args()

    broadcast_list = None
    if args.broadcast_addr is not None:
        broadcast_list = args.broadcast_addr.split(',')

    if args.ip:
        # do IP validation
        ip_pattern = \
            re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if not ip_pattern.match(args.ip):
            raise ValueError('IP address %s seems not a valid IP address!' % args.ip)

    if args.subcmd == 'show':
        CmdHandler(broadcast_list).show(args.verbose, args.ip)

    if args.subcmd == 'stats':
        CmdHandler(broadcast_list).stats()

    if args.subcmd == 'deploy':
        CmdHandler(broadcast_list).deploy()

    if args.subcmd == 'delete':
        CmdHandler(broadcast_list).delete(args.name, args.host)

    if args.subcmd == 'exec':
        CmdHandler(broadcast_list).exec_cmd(args.command, args.blocking)

    if args.subcmd == 'search':
        CmdHandler(broadcast_list).exec_search(args.keyword)

    if args.subcmd == 'console':
        CmdHandler(broadcast_list).exec_console(args.name, args.host)

    if args.subcmd == 'stop':
        CmdHandler(broadcast_list).exec_stop(args.name, args.host)

    if args.subcmd == 'start':
        CmdHandler(broadcast_list).exec_start(args.name, args.host)

    if args.subcmd == 'upgrade':
        exec_cmds = 'cd /kvm_images/tools/kvm-deployment;git pull;vmmanage setup'
        CmdHandler(broadcast_list).exec_cmd(exec_cmds, True)
