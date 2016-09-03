import os
import sys

from Utils import Utilities
from constant import *

__author__='rayer'

supported_type = ['invalid', 'scg', 'scge', 'vscg']


class InteractiveShell:

    args = ''

    def __init__(self, args):
        # Override arguments
        self.args = args

    def execute(self):
        self.__handle_branch()
        self.__handle_type()
        self.__handle_version()
        self.__handle_memory()
        self.__handle_ipv6()

    def __handle_type(self):
        check = False
        while not check:
            type_index = raw_input('SCG Type - 1. SCG 2. SCGE 3. vSCG : ')
            if type_index not in ['1', '2', '3']:
                print('Please select 1, 2 or 3!')
                continue

            self.args.type = supported_type[int(type_index)]
            check = True

    def __handle_branch(self):
        check = False
        support_branches = Utilities.get_supported_branches()
        while not check:

            for b in support_branches:
                print('%d : %s' % (support_branches.index(b) + 1, b))

            branch_index = raw_input('Select a branch : ')
            if branch_index == '0':
                print('No private local installation allow anymore, please use deploy_private')
            else:
                self.args.branch = support_branches[int(branch_index) - 1]
                check = True

    def __handle_version(self):

        if self.args.private:
            self.__handle_customized_image()
            return

        check = False
        supported_build = Utilities.get_branch_versions(self.args.branch, self.args.type)
        max_build = Utilities.get_most_recent_version(self.args.branch, self.args.type)

        while not check:
            version_input = raw_input('Enter version or \'i\' for version list [%s]: ' % max_build)
            if version_input is 'i':
                print('Available versions for %s of %s: ' %
                      (self.args.type, Utilities.get_branch_version_indicator(self.args.branch)))
                for build in supported_build:
                    sys.stdout.write('%d ' % build)
                print('')
            else:
                if version_input == '':
                    version_input = max_build

                if int(version_input) in supported_build:
                    check = True
                    self.args.build = version_input
                else:
                    print('Invalid build number, please input \'i\' for current build list')

    def __handle_memory(self):
        while True:
            memory_raw = raw_input('Allocate memory [%d] : ' % default_kvm_memory_allocated)
            if memory_raw == '':
                memory = default_kvm_memory_allocated
            else:
                memory = int(memory_raw)

            if memory in xrange(7, 49):
                self.args.memory = memory
                break
            continue

    def __handle_customized_image(self):

        check = False
        print('''
        You have selected to install customized image.
        Please upload your customized image to KVM server(I suggest under /tmp) and continue.
        For Kernel, if you don't know what it is, please leave it as blank.
        ''')
        while not check:
            if self.args.type != 'vscg':
                kernel_path = raw_input('Kernel Path(leave blank for default kernel) : ')
            image_path = raw_input('Image Path : ')

            # check path
            if kernel_path != '' and os.path.isfile(kernel_path) == False:
                print('Invalid kernel path!')
                continue

            if not os.path.isfile(image_path):
                print('Invalid image path!')
                continue

            self.args.kernel_path = kernel_path
            self.args.image_path = image_path
            check = True

    def __handle_ipv6(self):
        input = raw_input('Enable IPv6? [y/N]:')
        if input == 'y' or input == 'Y':
            print('IPV6 is enabled!')
            self.args.ipv6 = True
        else:
            print('IPv6 is disabled!')
