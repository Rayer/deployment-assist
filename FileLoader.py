import os
import sys
import urllib

import Utilities
import constant
import ipxe_server

__author__ = 'rayer'


class FileLoader:

    qcow_path = ''
    kernel_path = ''
    scg_image_path = ''

    def __init__(self):
        pass

    def execute_jenkins(self, scg_type, name, version, build):
        print('Init with %s (name: %s) %s@%s' % (scg_type, name, version, build))
        if scg_type == 'scg':
            self.handle_scg_files(name, version, build)
        elif scg_type == 'scge':
            self.handle_scge_files(name, version, build)
        elif scg_type == 'vscg':
            self.handle_vscg_files(name, version, build)
        else:
            print('No suitable module : %s' % scg_type)

    def execute_customized(self, scg_type, name, image_path, kernel_path=''):
        print('Customized SCG operations....')

        if os.path.isfile('/tmp/target.img') or os.path.islink('/tmp/target.img'):
            os.remove('/tmp/target.img')
        os.symlink(image_path, '/tmp/target.img')

        if kernel_path == '' and not os.path.isfile('/tmp/vmlinuz') and scg_type != 'vscg':
            raise BaseException('No /tmp/vmlinuz found! please copy one into /tmp')

        if kernel_path != '' and kernel_path != '/tmp/vmlinuz':
            if os.path.isfile('/tmp/vmlinuz') or os.path.islink('/tmp/vmlinuz'):
                os.remove('/tmp/vmlinuz')
            os.symlink(kernel_path, '/tmp/vmlinuz')
        self.qcow_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)

    def handle_vscg_files(self, name, version, build):

        print('Handling VSCG...')

        image_path = Utilities.get_file_path(version, 'vscg', 'image', build)

        print('\nDownloading qcow2 image : %s' % image_path)
        self.qcow_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)
        urllib.urlretrieve(image_path, self.qcow_path, self.__report_hook)

    def handle_scg_files(self, name, version, build):
        print('Handling SCG...')
        kernel_path = Utilities.get_file_path(version, 'scg', 'kernel', build)
        image_path = Utilities.get_file_path(version, 'scg', 'image', build)

        self.kernel_path = '/tmp/scg_vmlinuz'
        self.scg_image_path = '/tmp/scg_%s_image' % build
        self.qcow_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)

        print('\nDownloading kernel : %s' % kernel_path)
        urllib.urlretrieve(kernel_path, self.kernel_path, self.__report_hook)

        print('\nDownloading image : %s' % image_path)
        urllib.urlretrieve(image_path, self.scg_image_path, self.__report_hook)

        print('')
        if os.path.isfile('/tmp/target.img') or os.path.islink('/tmp/target.img'):
            os.remove('/tmp/target.img')
        os.symlink(self.scg_image_path, '/tmp/target.img')

        if os.path.isfile('/tmp/vmlinuz') or os.path.islink('/tmp/vmlinuz'):
            os.remove('/tmp/vmlinuz')
        os.symlink('scg_vmlinuz', '/tmp/vmlinuz')

    def handle_scge_files(self, name, version, build):
        print('Handling SCGE...')

        # version_resource = resource_map.get(version, None)
        # if version_resource is None:
        #     # handle error
        #     pass

        kernel_path = Utilities.get_file_path(version, 'scge', 'kernel', build)
        image_path = Utilities.get_file_path(version, 'scge', 'image', build)

        print('kernel path : %s' % kernel_path)
        print('image path : %s' % image_path)

        self.kernel_path = '/tmp/scge_vmlinuz'
        self.scg_image_path = '/tmp/scge_%s_image' % build
        self.qcow_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)

        print('\nDownloading kernel : %s' % kernel_path)
        urllib.urlretrieve(kernel_path, self.kernel_path, self.__report_hook)

        print('\nDownloading image : %s' % image_path)
        urllib.urlretrieve(image_path, self.scg_image_path, self.__report_hook)
        print('')

        if os.path.isfile('/tmp/target.img') or os.path.islink('/tmp/target.img'):
            os.remove('/tmp/target.img')
        os.symlink(self.scg_image_path, '/tmp/target.img')

        if os.path.isfile('/tmp/vmlinuz') or os.path.islink('/tmp/vmlinuz'):
            os.remove('/tmp/vmlinuz')
        os.symlink('scge_vmlinuz', '/tmp/vmlinuz')

    @staticmethod
    def __report_hook(chunk_order, chunk_size, total_size):
        if total_size < 1000:
            raise BaseException('File not found in path!')
        current_size = chunk_order * chunk_size
        receving_str = 'Downloading %f%% (%d/%d)' % ((float(current_size)/float(total_size)) * 100, current_size, total_size)
        sys.stdout.write("\r%s" % receving_str)
        sys.stdout.flush()








