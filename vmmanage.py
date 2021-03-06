#!/usr/bin/python
import argparse
import sys

import deploy
from Utils import Utilities
from Utils.ProfileUtils import ProfileParser, smart_dict

__author__ = 'rayer'


class VMManage:
    def __init__(self):
        pass

    def show_vms(self):
        vm_list = Utilities.get_vm_list()
        print('Online :')
        for online in vm_list['running']:
            p_parser = ProfileParser(online)
            online.update({'management_ip': p_parser.get_management_ip(), 'control_ip': p_parser.get_control_ip()})
            p_parser.get_status_color_print()(
                '[%(id)3s][%(status)-11s]:\t%(name)-30s\t%(type)5s\t%(build)5s@%(branch)-9s\t%(management_ip)-16s\t%(control_ip)-16s' % smart_dict(
                    online))

        print('')
        print('Offline :')
        for offline in vm_list['shutdown']:
            p_parser = ProfileParser(offline)
            p_parser.get_status_color_print()(
                '[%(id)3s][%(status)-11s]:\t%(name)-30s\t%(type)5s\t%(build)5s@%(branch)-9s' % smart_dict(offline))
        print('')

    def do_setup(self, syslink_only=False):
        Utilities.install_requirements()
        Utilities.setup_system_symbolic_links(sys.argv[0])
        if syslink_only is not True:
            Utilities.execute_setup_scripts(sys.argv[0])

    def delete_vm(self, vm_name=None):

        if vm_name:
            Utilities.del_vm(vm_name)
            return

        check = False

        while not check:
            in_vm_name = raw_input('Enter VM Name(? for vm list):')
            if in_vm_name == '?':
                self.show_vms()
                continue

            ret = Utilities.get_vm_status(in_vm_name)
            if ret is None:
                print("Invalid VM Name : %s" % in_vm_name)
                continue

            Utilities.del_vm(in_vm_name)
            check = True

    def create_vm(self, vm_name=None):

        if vm_name is None:
            vm_name = raw_input('VM Name : ')

        deploy.deploy([vm_name, '-i'])

    def start_vm(self, vm_name=None):
        if vm_name is not None:
            Utilities.start_vm(vm_name)
            return

        vm_list = Utilities.get_vm_list()

        count = 0
        for vm in vm_list['shutdown']:
            print('(%2d)%s' % (count, vm['name']))
            count += 1

        choice = raw_input('Choice : ')
        Utilities.start_vm(vm_list['shutdown'][int(choice)])

    def stop_vm(self, vm_name=None):
        if vm_name is not None:
            Utilities.stop_vm(vm_name)
            return

        vm_list = Utilities.get_vm_list()

        count = 0
        for vm in vm_list['running']:
            print('(%2d)%s' % (count, vm['name']))
            count += 1

        choice = raw_input('Choice : ')
        Utilities.stop_vm(vm_list['running'][int(choice)]['name'])

    def purgedb(self):
        Utilities.purge_db()

    def purge_storage(self):
        Utilities.purge_storage()


if __name__ == '__main__':

    v = VMManage()
    supported_cmds = ['show', 'create', 'delete', 'setup', 'stop', 'start', 'syslink', 'purge_db', 'purge_storage']

    parser = argparse.ArgumentParser(description='VM Customized Manager Wrapper')
    parser.add_argument('command', metavar='command',
                        choices=supported_cmds,
                        help='Commands : %s' % supported_cmds)
    parser.add_argument('vm_name', metavar='vm_name', nargs='?', help='VM Name', default=None)
    args = parser.parse_args()
    v = VMManage()

    if args.command == 'show':
        v.show_vms()

    if args.command == 'setup':
        v.do_setup()

    if args.command == 'syslink':
        v.do_setup(True)

    if args.command == 'delete':
        v.delete_vm(args.vm_name)

    if args.command == 'create':
        v.create_vm(args.vm_name)

    if args.command == 'start':
        v.start_vm(args.vm_name)

    if args.command == 'stop':
        v.stop_vm(args.vm_name)

    if args.command == 'purge_db':
        v.purgedb()

    if args.command == 'purge_storage':
        v.purge_storage()
