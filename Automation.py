import subprocess
import sys
import time

import pexpect
import xml.etree.ElementTree as ET
import os

import Utilities
import constant
import ipxe_server

__author__ = 'rayer'


class Automation:
    name = ''

    def __init__(self, type, name, ipv6):
        self.name = name
        self.type = type
        self.ipv6 = ipv6

    def execute(self):
        if self.type == 'vscg':
            self.execute_vscg()
        elif self.type == 'scg':
            self.execute_scg()
        elif self.type == 'scge':
            self.execute_scge()
        else:
            print('Not support type %s yet!' % self.type)
            print('Wait 60 sec for ipxe down...')
            self.__prompt_pause(60)

    '''
    Automation SCG requires follow steps :
    1. (Optional) Make a valid boot_kvm.ipxe and build iso with this embedded script
       Because of restriction, currently boot path needed to be 10.x(first configurable NIC)
    2. (Optional) Copy .iso to destination directory
    (Code Snippet) virt-install --name R-SCG --ram 16384 --vcpus=8 --os-type=linux --os-variant=rhel6 --vnc --hvm --disk path=/kvm_images//R-SCG.qcow2,device=disk,format=qcow2,size=50,bus=sata --cdrom=/kvm_images/ipxe.iso --boot cdrom,hd --network bridge=bridge1,model=virtio --network bridge=bridge1,model=virtio --network bridge=bridge0,model=virtio
    3. Wait 600 sec, or peek virsh domain list. The installation will turn off itself.
    4. Start regular SCG/SCGE automation install
    '''

    def execute_scg(self):

        self.__handle_scg_stage1()

        c = pexpect.spawn('virsh console %s' % self.name, timeout=1000)
        c.logfile = sys.stdout
        c.setecho(False)

        self.__do_scg_login(c, 'admin', 'admin')

        c.expect('#')
        c.sendline('rbd Gallus SCG200 00000089 11:22:33:88:44:22 32 ruckus')

        c.expect('#')
        c.sendline('setup')

        # This part will decide use ipv6 or not, let use ipv6
        c.expect(['Select address type'])
        if self.ipv6:
            c.sendline('2')
        else:
            c.sendline('1')

        # IPv4, control
        c.expect(['Select IP configuration'])
        c.sendline('2')
        c.expect(['Are these correct'])
        c.sendline('y')

        # IPv4, cluster
        c.expect(['Select IP configuration'])
        c.sendline('2')
        c.expect(['Are these correct'])
        c.sendline('y')

        # IPv4, management
        c.expect(['Select IP configuration'])
        c.sendline('2')
        c.expect(['Are these correct'])
        c.sendline('y')

        c.expect(['Select system default gateway'])
        c.sendline('Management')
        c.expect(['Primary'])
        c.sendline('8.8.8.8')
        c.sendline('8.8.4.4')

        # Prior from 3.1, it doesn't have this
        c.expect(['Control NAT', pexpect.TIMEOUT], timeout=12)
        c.sendline('')

        if self.ipv6:
            # IPv6, control
            c.expect(['Select IP configuration'])
            c.sendline('1')
            c.sendline('1111:2222:6666::5566/64')
            c.sendline('1111:2222:6666::0000')
            c.sendline('y')

            # IPv6, management
            c.expect(['Select IP configuration'])
            c.sendline('1')
            c.sendline('4444:3333:6666::5566/64')
            c.sendline('4444:3333:6666::0000')
            c.sendline('y')

            c.expect(['Select system default gateway'])
            c.sendline('Management')
            c.expect(['Primary'])
            c.sendline('')

        c.expect(['Enter "restart network" or press Enter'])
        c.sendline('')

        c.expect(['>', '#'])
        # 2nd time setup
        c.sendline('setup')
        c.sendline('')

        c.expect('Do you want to setup network?')
        c.sendline('')
        c.expect('an exist cluster')
        c.sendline('c')
        c.expect('Cluster Name')
        c.sendline(Utilities.convert_blade_preferred_characters(self.name))
        c.expect('Controller Description:')
        c.sendline('Automatic installed %s' % self.name)
        c.expect('Are these correct')
        c.sendline('y')
        c.expect('Enter the controller name of the blade')
        c.sendline('%s-C' % Utilities.convert_blade_preferred_characters(self.name))

        # Sometimes NTP Server can't be reached...
        c.expect('NTP Server ')
        c.sendline('')

        index = c.expect(['Cannot synchronize', 'APs automatically'])
        if index == 0:
            c.sendline('')
            c.sendline('')
            c.sendline('')
            c.expect('APs automatically')
        else:
            pass
        c.sendline('')
        c.expect('Enter admin password:')
        c.sendline('admin!234')
        c.sendline('admin!234')
        c.sendline('admin!234')
        c.sendline('admin!234')

        c.expect('Please login again.', timeout=1200)
        print('Installation finished!')
        c.sendline('')

        self.__do_scg_login(c, 'admin', 'admin!234')
        # self.__do_sesame2(c)
        c.sendline('exit')

        # TODO : Requires a callback hook

        # TODO : Modify /opt/ruckuswireless/wsg/cli/conf/cassandra.yaml

    def execute_scge(self):

        self.__handle_scg_stage1()

        c = pexpect.spawn('virsh console %s' % self.name, timeout=1000)
        c.logfile = sys.stdout
        c.setecho(False)

        self.__do_scg_login(c, 'admin', 'admin')
        c.expect('#')
        c.sendline('rbd Gallus SZ124 00000089 11:22:33:88:44:22 32 ruckus')
        c.expect('#')
        c.sendline('setup')

        # Have yet supported IPV6 for SCGE
        # c.expect(['Select address type'])
        # if self.ipv6:
        #     c.sendline('2')
        # else:
        #     c.sendline('1')

        # IPv4, management

        # Support 1 group only for now
        c.expect(['Port Grouping Configuration'])
        c.sendline('1')

        c.expect(['Select IP configuration'])
        c.sendline('2')
        c.expect(['Are these correct'])
        c.sendline('y')

        c.expect(['Primary'])
        c.sendline('8.8.8.8')
        c.sendline('8.8.4.4')

        # Prior from 3.1, it doesn't have this
        c.expect(['Control NAT', pexpect.TIMEOUT], timeout=12)
        c.sendline('')

        c.expect('an exist cluster')
        c.sendline('c')
        c.expect('Cluster Name')
        c.sendline(Utilities.convert_blade_preferred_characters(self.name))
        c.expect('Controller Description:')
        c.sendline('Automatic installed %s' % self.name)
        c.expect('Are these correct')
        c.sendline('y')
        c.expect('Enter the controller name of the blade')
        c.sendline('%s-C' % Utilities.convert_blade_preferred_characters(self.name))

        # Sometimes NTP Server can't be reached...
        c.expect('NTP Server ')
        c.sendline('')

        index = c.expect(['Cannot synchronize', 'APs automatically'])
        if index == 0:
            c.sendline('')
            c.sendline('')
            c.sendline('')
            c.expect('APs automatically')
        else:
            pass

        c.sendline('n')
        c.expect('Enter admin password:')
        c.sendline('admin!234')
        c.sendline('admin!234')
        c.sendline('admin!234')
        c.sendline('admin!234')

        c.expect('Please login again.', timeout=1200)
        print('Installation finished!')
        c.sendline('')

        self.__do_scg_login(c, 'admin', 'admin!234')
        # self.__do_sesame2(c)
        c.sendline('exit')

    def execute_vscg(self):
        print('Executing VSCG Automatic Setup....')
        # VSCG need somehow bigger timeout, or setup process will cause timeout
        c = pexpect.spawn('virsh console %s' % self.name, timeout=1000)
        c.logfile = sys.stdout
        c.setecho(False)
        self.__do_scg_login(c, 'admin', 'admin')
        c.expect('#')
        c.sendline('setup')

        # This part will decide use high scale or essencial, let's fix it into high scale first.
        index = c.expect(['High', 'Enter vSCG Model'])
        if index == 0:
            c.sendline('2')
        else:
            c.sendline('Carrier')

        # This part will decide use ipv6 or not, let use ipv6
        c.expect(['Select address type'])
        if self.ipv6:
            c.sendline('2')
        else:
            c.sendline('1')

        # IPv4, control
        c.expect(['Select IP configuration'])
        c.sendline('2')
        c.expect(['Are these correct'])
        c.sendline('y')

        # IPv4, cluster
        c.expect(['Select IP configuration'])
        c.sendline('2')
        c.expect(['Are these correct'])
        c.sendline('y')

        # IPv4, management
        c.expect(['Select IP configuration'])
        c.sendline('2')
        c.expect(['Are these correct'])
        c.sendline('y')

        c.expect(['Select system default gateway'])
        c.sendline('Management')
        c.expect(['Primary'])
        c.sendline('8.8.8.8')
        c.sendline('8.8.4.4')

        # Prior to 3.1, it is not exists.
        c.expect(['Control NAT', pexpect.TIMEOUT], timeout=12)
        c.sendline('')

        if self.ipv6:
            # IPv6, control
            c.expect(['Select IP configuration'])
            c.sendline('1')
            c.sendline('1111:2222:6666::5566/64')
            c.sendline('1111:2222:6666::0000')
            c.sendline('y')

            # IPv6, management
            c.expect(['Select IP configuration'])
            c.sendline('1')
            c.sendline('4444:3333:6666::5566/64')
            c.sendline('4444:3333:6666::0000')
            c.sendline('y')

            c.expect(['Select system default gateway'])
            c.sendline('Management')
            c.expect(['Primary'])
            c.sendline('')

        c.expect(['Enter "restart network" or press Enter'])
        c.sendline('')

        c.expect(['>', '#'])
        # 2nd time setup
        c.sendline('setup')
        c.sendline('')

        c.expect('Do you want to setup network?')
        c.sendline('')
        c.expect('an exist cluster')
        c.sendline('c')
        c.expect('Cluster Name')
        c.sendline(Utilities.convert_blade_preferred_characters(self.name))
        c.expect('Controller Description:')
        c.sendline('Automatic installed %s' % self.name)
        c.expect('Are these correct')
        c.sendline('y')
        c.expect('Enter the controller name of the blade')
        c.sendline('%s-C' % Utilities.convert_blade_preferred_characters(self.name))
        c.expect('NTP Server ')
        c.sendline('')
        index = c.expect(['Cannot synchronize', 'APs automatically'])
        if index == 0:
            c.sendline('')
            c.sendline('')
            c.sendline('')
            c.expect('APs automatically')
        c.sendline('')
        c.expect('Enter admin password:')
        c.sendline('admin!234')
        c.sendline('admin!234')
        c.sendline('admin!234')
        c.sendline('admin!234')

        c.expect('Please login again.', timeout=1200)
        c.sendline('')
        self.__do_scg_login(c, 'admin', 'admin!234')
        # self.__do_sesame2(c)

        print('Installation finished!')

    def __do_scg_login(self, c, login, password):
        c.expect(['login: '])
        c.sendline(login)
        c.expect(['Password: '])
        c.sendline(password)
        c.expect(['>'])
        c.sendline('en')
        c.sendline(password)

    def __do_setup_ipv4(self):
        pass

    def __do_setup_ipv6(self):
        pass

    def __do_sesame2(self, c):
        c.sendline('show version')
        c.expect(['>', '#'])
        serial = ''
        version_raw = c.readline()
        print('Parsing Serial...\n%s' % version_raw)
        for line in version_raw.split('\n'):
            if 'Serial' not in line:
                continue
            serial = line.split(':')[1].strip()
            print('Parsed serial : %s' % serial)
            break

        sesame2 = Utilities.get_sesame2(serial)
        c.sendline('debug')
        c.sendline('save passphrase')
        c.sendline('exit')
        c.expect('#')
        c.sendline('!v54!')
        c.expect('Passphrase')
        c.sendline(sesame2)
        c.expect('bash')

    def __prompt_pause(self, time_sec):
        timer = time_sec
        while timer != 0:
            time.sleep(1)
            sys.stdout.write('\rTime remaining : %d s' % timer)
            sys.stdout.flush()
            timer -= 1
        print('Time up!')

    def __handle_scg_stage1(self):

        if self.type == 'scge':
            print('installation type is SCGE, patching network interface defination...')
            self.__patch_scge_nic()

        timer = constant.scg_installation_wait_time
        print('Waiting for installation completed...')
        print('Start \'virsh-console\' in %d sec' % timer)
        self.__prompt_pause(timer)

        print('\nStarting Virsh.....')
        # system('virsh start %s' % self.name)



        while subprocess.call(['virsh', 'start', self.name]) != 0:
            print('Domain %s seems still in installation process, wait for another 30 sec' % self.name)
            self.__prompt_pause(30)

        # After stage 1 completed, turn off iPXE server
        print('Shutting down embedded iPXE Server....')
        ipxe_server.cleanup_ipxe_thread()

    def __patch_scge_nic(self):
        config = subprocess.check_output(['virsh', 'dumpxml', self.name])
        tree = ET.fromstring(config)

        # Need to do twice, dunno why...
        for interface in tree.iter('interface'):
            if interface.find('source').attrib['bridge'] == 'bridge1':
                tree.find('devices').remove(interface)

        for interface in tree.iter('interface'):
            if interface.find('source').attrib['bridge'] == 'bridge1':
                tree.find('devices').remove(interface)

        # Write code to /tmp/<DomainName>
        file_name = '/tmp/%s.xml' % self.name
        with open(file_name, 'w') as conf_file:
            conf_file.write(ET.tostring(tree))

        print(subprocess.check_output(['virsh', 'define', file_name]))
        os.remove(file_name)