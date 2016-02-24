import os
import sys
import urllib

import Utilities
import constant
from Utils.database import open_scg_dao

__author__ = 'rayer'


class FileLoader:
    local_qcow2_path = ''
    local_kernel_path = ''
    local_img_path = ''

    def __init__(self):
        pass

    def execute_jenkins(self, scg_profile):

        # print('Init with %s (name: %s) %s@%s' % (scg_type, name, version, build))
        print('Init with %(type)s (name: %(name)s) %(branch)s@%(build)s' % scg_profile)
        scg_type = scg_profile['type']
        if scg_type == 'scg':
            self.handle_scg_files(scg_profile)
        elif scg_type == 'scge':
            self.handle_scge_files(scg_profile)
        elif scg_type == 'vscg':
            self.handle_vscg_files(scg_profile)
        else:
            print('No suitable module : %s' % scg_type)

    def execute_customized(self, scg_profile):
        print('Customized SCG operations....')
        scg_profile.update({'status': 'downloading'})
        with open_scg_dao() as dao:
            dao.update(scg_profile)

        image_path = scg_profile['image_path']
        kernel_path = scg_profile['kernel_path']
        scg_type = scg_profile['type']
        name = scg_profile['name']

        if os.path.isfile('/tmp/target.img') or os.path.islink('/tmp/target.img'):
            os.remove('/tmp/target.img')
        os.symlink(image_path, '/tmp/target.img')

        if kernel_path == '' and not os.path.isfile('/tmp/vmlinuz') and scg_type != 'vscg':
            raise BaseException('No /tmp/vmlinuz found! please copy one into /tmp')

        if kernel_path != '' and kernel_path != '/tmp/vmlinuz':
            if os.path.isfile('/tmp/vmlinuz') or os.path.islink('/tmp/vmlinuz'):
                os.remove('/tmp/vmlinuz')
            os.symlink(kernel_path, '/tmp/vmlinuz')
        self.local_qcow2_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)

    def handle_vscg_files(self, scg_profile):

        name = scg_profile['name']
        version = scg_profile['branch']
        build = scg_profile['build']

        print('Handling VSCG...')

        image_path = Utilities.get_file_path(version, 'vscg', 'image', build)

        print('\nDownloading qcow2 image : %s' % image_path)
        self.local_qcow2_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)
        urllib.urlretrieve(image_path, self.local_qcow2_path, self.__report_hook)

    def handle_scg_files(self, scg_profile):

        name = scg_profile['name']
        version = scg_profile['branch']
        build = scg_profile['build']

        print('Handling SCG...')
        kernel_path = Utilities.get_file_path(version, 'scg', 'kernel', build)
        image_path = Utilities.get_file_path(version, 'scg', 'image', build)

        self.local_kernel_path = '/tmp/scg_vmlinuz'
        self.local_img_path = '/tmp/scg_%s_image' % build
        self.local_qcow2_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)

        print('\nDownloading kernel : %s' % kernel_path)
        urllib.urlretrieve(kernel_path, self.local_kernel_path, self.__report_hook)

        print('\nDownloading image : %s' % image_path)
        urllib.urlretrieve(image_path, self.local_img_path, self.__report_hook)

        print('')
        if os.path.isfile('/tmp/target.img') or os.path.islink('/tmp/target.img'):
            os.remove('/tmp/target.img')
        os.symlink(self.local_img_path, '/tmp/target.img')

        if os.path.isfile('/tmp/vmlinuz') or os.path.islink('/tmp/vmlinuz'):
            os.remove('/tmp/vmlinuz')
        os.symlink('scg_vmlinuz', '/tmp/vmlinuz')

    def handle_scge_files(self, scg_profile):
        print('Handling SCGE...')

        name = scg_profile['name']
        version = scg_profile['branch']
        build = scg_profile['build']

        kernel_path = Utilities.get_file_path(version, 'scge', 'kernel', build)
        image_path = Utilities.get_file_path(version, 'scge', 'image', build)

        print('kernel path : %s' % kernel_path)
        print('image path : %s' % image_path)

        self.local_kernel_path = '/tmp/scge_vmlinuz'
        self.local_img_path = '/tmp/scge_%s_image' % build
        self.local_qcow2_path = '%s/%s.qcow2' % (constant.vm_storage_path, name)

        print('\nDownloading kernel : %s' % kernel_path)
        urllib.urlretrieve(kernel_path, self.local_kernel_path, self.__report_hook)

        print('\nDownloading image : %s' % image_path)
        urllib.urlretrieve(image_path, self.local_img_path, self.__report_hook)
        print('')

        if os.path.isfile('/tmp/target.img') or os.path.islink('/tmp/target.img'):
            os.remove('/tmp/target.img')
        os.symlink(self.local_img_path, '/tmp/target.img')

        if os.path.isfile('/tmp/vmlinuz') or os.path.islink('/tmp/vmlinuz'):
            os.remove('/tmp/vmlinuz')
        os.symlink('scge_vmlinuz', '/tmp/vmlinuz')

    def local_storage_params(self):
        return {
            'qcow2_path': self.local_qcow2_path,
            'image_path': self.local_img_path,
            'kernel_path': self.local_kernel_path
        }

    @staticmethod
    def __report_hook(chunk_order, chunk_size, total_size):
        if total_size < 1000:
            raise BaseException('File not found in path!')
        current_size = chunk_order * chunk_size
        receving_str = 'Downloading %f%% (%d/%d)' % ((float(current_size)/float(total_size)) * 100, current_size, total_size)
        sys.stdout.write("\r%s" % receving_str)
        sys.stdout.flush()








