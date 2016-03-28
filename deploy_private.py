#!/usr/bin/python
import os.path

__author__ = 'rayer'

if __name__ == '__main__':

    print('''
    Welcome to Deploy Assist Private Build Utility!
    Please be noted that this application currently only support SCG/SZ100(1nic profile)
    ''')

    use_default = False
    try:
        from Comm.Broadcaster import Broadcaster
        from Comm.Cmds import *

        vm_map = []
        vm_list = Broadcaster().broadcast(GetVMList())
        for vm_info in vm_list:
            vm_map.append((vm_info[0]['host'], vm_info[1][0]))
        if vm_map.__len__() <= 0:
            raise BaseException('No server response for getting VMs, use default!')
    except BaseException as B:
        print(B)
        vm_map = (
            ('KVM01', '172.17.61.127'),
            ('KVM02', '172.17.61.128'),
            ('KVM03', '172.17.61.129'),
            ('KVM04', '172.17.61.130'),
            ('KVM05', '172.17.61.131'),
        )
        use_default = True

    print('Using VMs map as below : ')
    print(vm_map)
    name = raw_input('VM Name:')

    defImage = None
    while True:
        # Find if current directory contains a .img file
        for file_in_dir in os.listdir(os.curdir):
            if file_in_dir.endswith('.img'):
                defImage = file_in_dir
                break
        if defImage is not None:
            img_path = raw_input('Image Path[%s]:' % defImage)
            if img_path == '':
                img_path = defImage
        else:
            img_path = raw_input('Image Path : ')

        if not os.path.isfile(img_path):
            print('Invalid image path!')
            continue
        break

    scg_type_list = ('scg', 'scge')

    defTarget = 'scg'
    if img_path.startswith('scge'):
        defTarget = 'scge'

    defKernel = None
    while True:
        defKernel = os.path.dirname(img_path) + 'vmlinuz'
        if os.path.isfile(defKernel):
            kernel_path = raw_input('Kernel Path [%s] : ' % defKernel)
            if kernel_path == '':
                kernel_path = defKernel
        else:
            kernel_path = raw_input('Kernel Path : ')

        if os.path.isfile(kernel_path):
            break
        else:
            print('Invalid kernel path!')
            continue

    while True:
        scg_type = raw_input('Image type (scg/scge) [%s]:' % defTarget)
        if scg_type == '':
            scg_type = defTarget

        if scg_type not in scg_type_list:
            print('Invalid SCG type!')
            continue
        else:
            break

    extra_options = raw_input('Extra options(Please leave it blank if you don\'t know what it is):')
    sanity_test = raw_input('Is it build for sanity test[y/N] :')

    if sanity_test.lower() == 'y':
        extra_options += ' --sanity_test'
        email = raw_input('Notification email : ')
        extra_options += ' --email {}'.format(email)

    index = 0

    if use_default is True:
        for (kvm_name, ip) in vm_map:
            print('[%(index)d]\t%(ip)s(%(name)s)' % {'index': index, 'ip': ip, 'name': kvm_name})
            index += 1
    else:
        for server_info in vm_list:
            server_info[0].update({'ip': server_info[1][0], 'index': index})
            index += 1
            print(
            '({p[index]})\t{p[ip]}({p[host]})\tRunning:{running_count}\tShutdown:{shutdown_count}'.format(
                p=server_info[0], running_count=len(server_info[0]['running']),
                shutdown_count=len(server_info[0]['shutdown'])))

    choice = int(raw_input('Choice:'))
    target_kvm = vm_map[choice][1]

    print('''

Image path : %s
Kernel path : %s
Target KVM : %s

Installation start. If it asks root password, please consider adding your public key to server.

    ''' % (img_path, kernel_path, target_kvm))

    # scp files to server
    cmd = 'scp %s root@%s:/tmp/'
    param = {'name': name, 'ip': target_kvm, 'kernel': kernel_path, 'img': img_path,
             'extra': extra_options, 'type': scg_type}

    scp_kernel_cmd = 'scp %(kernel)s root@%(ip)s:/tmp/%(name)s_vmlinuz' % param
    scp_image_cmd = 'scp %(img)s root@%(ip)s:/tmp/%(name)s_%(type)s.img' % param
    ssh_cmd = 'ssh root@%(ip)s -C \'cd /tmp;deploy %(name)s --private -t %(type)s --kernel_path /tmp/%(name)s_vmlinuz \
        --image_path /tmp/%(name)s_%(type)s.img %(extra)s -f \'' % param

    cmd_list = (scp_kernel_cmd, scp_image_cmd, ssh_cmd)
    for cmd in cmd_list:
        print('Executing : %s' % cmd)
        os.system(cmd)
