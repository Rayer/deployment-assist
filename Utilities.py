import httplib
import os
import re
import subprocess
import urllib2

from BeautifulSoup import BeautifulSoup

import configuration
import constant
from Utils.ProfileUtils import ProfileParser
from Utils.database import open_scg_dao

__author__ = 'rayer'


def __get_master():
    return constant.resource_map.get('master')


def __get_branch(branch_name):
    return __get_branches_raw().get(branch_name)


def __get_branches_raw():
    return constant.resource_map.get('branches')


def __get_root(branch, variant):
    return __get_variant(branch, variant).get('root')


def __get_variants_raw(branch):
    return __get_branch(branch).get('variants')


def __get_variant(branch, variant):
    return __get_variants_raw(branch).get(variant)


def __get_version_string(branch):
    return __get_branch(branch).get('version')


def get_branch_version_indicator(branch):
    return __get_version_string(branch).replace('{$build}', '*')


def get_supported_branches():
    return __get_branches_raw().keys()


def get_branch_supported_scg_type(branch):
    return __get_variants_raw(branch).keys()


def __get_file_path_raw(branch, variant, file_type):
    return __get_variant(branch, variant).get(file_type)


def get_file_path(branch, variant, file_type, build):
    # extend root first
    return __get_file_path_raw(branch, variant, file_type) \
        .replace('{$root}', __get_root(branch, variant)) \
        .replace('{$version}', __get_version_string(branch)) \
        .replace('{$build}', build) \
        .replace('{$master}', __get_master())


def get_root_path(branch, scg_type):
    raw = constant.resource_map.get('branches').get(branch).get('variants').get(scg_type).get('root')
    return raw.replace('{$master}', __get_master())


def convert_blade_preferred_characters(origin):
    output = ''
    pattern = re.compile('[A-Za-z0-9-]')
    for c in origin:
        if pattern.match(c):
            output += c
        else:
            output += '-'

    return output


# TODO: Extract these 2 methods

def get_branch_versions(branch, variant):
    target_url = get_root_path(branch, variant)
    result = urllib2.urlopen(target_url)
    soup = BeautifulSoup(result)
    ret = []
    version_pattern_raw = __get_version_string(branch).replace('.', '\.').replace('{$build}', '\d')
    version_pattern = re.compile(version_pattern_raw)
    for element in soup.findAll('a'):
        if version_pattern.match(element.text):
            ret.append(int(element.text.split('.')[-1].replace('/', '')))
            ret.sort()

    return ret


def get_branch_download_dirs(branch, variant):
    target_url = get_root_path(branch, variant)
    result = urllib2.urlopen(target_url)
    soup = BeautifulSoup(result)
    ret = []
    version_pattern_raw = __get_version_string(branch).replace('.', '\.').replace('{$build}', '\d')
    version_pattern = re.compile(version_pattern_raw)
    for element in soup.findAll('a'):
        if version_pattern.match(element.text):
            ret.append(element['href'])

    return ret


def get_sesame2(serial):
    h = httplib.HTTPConnection('172.17.25.219')
    h.request('GET', '/passphrase.php?serial=%s' % serial)
    res = h.getresponse().read()
    # print('Parsed Sesame2 result : %s ' % res)
    return res.split('\'')[1]


def setup_system_symbolic_links(script_bin_path):
    rp = os.path.realpath(script_bin_path)
    print('realpath : %s' % rp)
    for (source, target) in configuration.symbolic_link_map:
        print('Linking %(source)s to %(target)s ...' % {'source': os.path.dirname(rp) + '/' + source, 'target': target})
        if os.path.islink(target):
            os.remove(target)

        if os.path.isfile(target):
            raise BaseException('%s is occupied by file' % target)

        os.symlink(os.path.dirname(rp) + '/' + source, target)


def execute_setup_scripts(script_bin_path):
    rp = os.path.realpath(script_bin_path)
    for (cmd, daemonized) in configuration.init_exec:
        if daemonized:
            os.system('nohup python %s &' % (os.path.dirname(rp) + '/' + cmd))
        else:
            os.system('python %s' % os.path.dirname(rp) + '/' + cmd)


def get_vm_list():
    ret_list = subprocess.check_output(['virsh', 'list', '--all']).splitlines()
    ret = {'running': [], 'shutdown': []}
    for seq in ret_list[2:]:  # Pass first two lines
        data = seq.split()

        if data.__len__() < 1:
            break

        isRunning = data[0] != '-'

        with open_scg_dao() as dao:
            profile = dao.read(data[1])

        ret_data = {
            'id': '-' if data[0] == '-' else data[0],
            'name': data[1]
        }

        if profile is not None:
            parser = ProfileParser(profile)
            additional_data = {
                'management': parser.get_management_ip(),
                'branch': parser.get_branch(),
                'type': parser.get_type(),
                'build': parser.get_build()
            }
            ret_data.update(additional_data)

        if isRunning:
            ret['running'].append(ret_data)
        else:
            ret['shutdown'].append(ret_data)

    return ret


def get_host_stats():
    ret_list = subprocess.check_output(['virsh', 'nodememstats']).splitlines()
    mem = {}
    for seq in ret_list:
        if ':' not in seq:
            continue
        pair = seq.split(':')
        mem[pair[0].strip()] = pair[1].strip()

    vm_list = get_vm_list()
    vms = {'running': len(vm_list['running']), 'shutdown': len(vm_list['shutdown'])}
    ret = {}
    ret.update(mem)
    ret.update(vms)
    return ret


def del_vm(vm_name):
    vm_list = get_vm_list()
    vm_exist = False

    # if running, destroy it
    for vm in vm_list['running']:
        if vm_name == vm['name']:
            os.system('virsh destroy %s' % vm_name)
            vm_exist = True
            vm_list = get_vm_list()  # Get VM List again
            break
        elif vm_name == vm['id']:
            vm_name = vm['name']
            os.system('virsh destroy %s' % vm_name)
            vm_exist = True
            vm_list = get_vm_list()

    for vm in vm_list['shutdown']:
        if vm_name == vm['name']:
            os.system('virsh undefine %s' % vm_name)
            vm_exist = True
            break

    if vm_exist:
        path = constant.vm_storage_path + vm_name + '.qcow2'
        print('deleting file : %s' % path)
        os.remove(path)
        with open_scg_dao() as dao:
            dao.delete(vm_name)
    else:
        raise Exception('VM %(vm_name)s is not exist!' % {'vm_name': vm_name})


def start_vm(vm_name):
    vm_list = get_vm_list()
    # if in running, throw error message
    for vm_info in vm_list['running']:
        if vm_name == vm_info['name']:
            raise ValueError('VM %s already in running state!' % vm_name)

    for vm in vm_list['shutdown']:
        if vm['name'] == vm_name:
            os.system('virsh start %s' % vm_name)
            with open_scg_dao() as dao:
                profile = dao.read(vm_name)
                if profile is not None:
                    profile.update({'status': 'running'})
                    dao.update(profile)
            return

    raise ValueError('Can\'t find VM %s !' % vm_name)


def stop_vm(vm_name):
    vm_list = get_vm_list()
    for vm_info in vm_list['running']:
        if vm_name == vm_info['id'] or vm_name == vm_info['name']:
            os.system('virsh destroy %s' % vm_info['name'])
            with open_scg_dao() as dao:
                profile = dao.read(vm_name)
                if profile is not None:
                    profile.update({'ip': None, 'status': 'stopped'})
                    dao.update(profile)
            return

    for vm in vm_list['stop']:
        if vm['name'] == vm_name:
            raise ValueError('VM %s is already stopped!')

    raise ValueError('VM %s is not found!')


def get_vm_status(vm_name):
    vm_list = get_vm_list()

    for vm in vm_list['running']:
        if vm_name == vm['name'] or vm_name == vm['id']:
            return 'running'

    for vm in vm_list['shutdown']:
        if vm_name == vm['name']:
            return 'shutdown'

    return None


def pid_lock_utils(pidfile, main_logic):
    pid = str(os.getpid())

    if os.path.isfile(pidfile):
        with open(pidfile, 'r') as file:
            old_pid = file.read(6)
        print('Service is already running at %s, deleting this and restart service' % old_pid)
        try:
            os.kill(int(old_pid), 9)
        except OSError as e:
            print('Seems there is some trouble deleting %s' % old_pid)
        finally:
            os.remove(pidfile)

    with open(pidfile, 'w') as file:
        print('Application starts as pid : %s' % pid)
        file.write(pid)

    try:
        main_logic()
    finally:
        os.remove(pidfile)


def install_requirements():
    os.system('pip install --upgrade pip')
    os.system('pip install -U -r requirements.txt')
