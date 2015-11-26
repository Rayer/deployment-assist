#!/usr/bin/python
import argparse
import sys
import Utilities

__author__ = 'rayer'


class VMManage:
    def __init__(self):
        pass

    def show_vms(self):
        vm_list = Utilities.get_vm_list()
        print('Online :')
        for online in vm_list['running']:
            print('[%s]:\t%s' % (online['id'], online['name']))

        print('')
        print('Offline :')
        for offline in vm_list['shutdown']:
            print('%s' % offline)
        print('')

    def do_syslink(self):
        Utilities.setup_system_symbolic_links(sys.argv[0])

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='VM Customized Manager Wrapper')
    parser.add_argument('command', metavar='command', choices=['show', 'create', 'delete', 'syslink'], help='Commands : show, create, delete, syslink')
    parser.add_argument('vm_name', metavar='vm_name', nargs='?', help='VM Name', default=None)
    args = parser.parse_args()
    v = VMManage()

    if args.command == 'show':
        v.show_vms()

    if args.command == 'syslink':
        v.do_syslink()

    if args.command == 'delete':
        v.delete_vm(args.vm_name)
