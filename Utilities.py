import httplib
import os
import re
import subprocess
import urllib2

from BeautifulSoup import BeautifulSoup

import Utilities
import configuration
import constant

__author__ = 'rayer'


def __get_master():
    return constant.resource_map.get('master')


def __get_branch(branch_name):
    return Utilities.__get_branches_raw().get(branch_name)


def __get_branches_raw():
    return constant.resource_map.get('branches')


def __get_root(branch, variant):
    return Utilities.__get_variant(branch, variant).get('root')


def __get_variants_raw(branch):
    return Utilities.__get_branch(branch).get('variants')


def __get_variant(branch, variant):
    return Utilities.__get_variants_raw(branch).get(variant)


def __get_version_string(branch):
    return Utilities.__get_branch(branch).get('version')


def get_branch_version_indicator(branch):
    return Utilities.__get_version_string(branch).replace('{$build}', '*')


def get_supported_branches():
    return Utilities.__get_branches_raw().keys()


def get_branch_supported_scg_type(branch):
    return Utilities.__get_variants_raw(branch).keys()


def __get_file_path_raw(branch, variant, file_type):
    return Utilities.__get_variant(branch, variant).get(file_type)


def get_file_path(branch, variant, file_type, build):
    # extend root first
    return Utilities.__get_file_path_raw(branch, variant, file_type) \
        .replace('{$root}', Utilities.__get_root(branch, variant)) \
        .replace('{$version}', Utilities.__get_version_string(branch)) \
        .replace('{$build}', build) \
        .replace('{$master}', Utilities.__get_master())


def get_root_path(branch, scg_type):
    raw = constant.resource_map.get('branches').get(branch).get('variants').get(scg_type).get('root')
    return raw.replace('{$master}', Utilities.__get_master())


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
    target_url = Utilities.get_root_path(branch, variant)
    result = urllib2.urlopen(target_url)
    soup = BeautifulSoup(result)
    ret = []
    version_pattern_raw = Utilities.__get_version_string(branch).replace('.', '\.').replace('{$build}', '\d')
    version_pattern = re.compile(version_pattern_raw)
    for element in soup.findAll('a'):
        if version_pattern.match(element.text):
            ret.append(int(element.text.split('.')[-1].replace('/', '')))
            ret.sort()

    return ret


def get_branch_download_dirs(branch, variant):
    target_url = Utilities.get_root_path(branch, variant)
    result = urllib2.urlopen(target_url)
    soup = BeautifulSoup(result)
    ret = []
    version_pattern_raw = Utilities.__get_version_string(branch).replace('.', '\.').replace('{$build}', '\d')
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


'''
format :
{'running':[{'id':2, 'name':'SCG34-SCG'}, {'id':6, 'name':'Dora-scg-34-2224'}],
 'shutdown':['JasmineSCG', 'Kali-Penetration-TB02']}
'''


def get_vm_list():
    ret_list = subprocess.check_output(['virsh', 'list', '--all']).splitlines()
    ret = {'running': [], 'shutdown': []}
    for seq in ret_list[2:]:  # Pass first two lines
        data = seq.split()

        if data.__len__() < 1:
            break

        if data[0] == '-':
            ret['shutdown'].append(data[1])
        else:
            ret['running'].append({'id': data[0], 'name': data[1]})

    return ret


def del_vm(vm_name):
    vm_list = Utilities.get_vm_list()
    vm_exist = False

    # if running, destroy it
    for vm in vm_list['running']:
        if vm_name == vm['name']:
            os.system('virsh destroy %s' % vm_name)
            vm_exist = True
            vm_list = Utilities.get_vm_list()  # Get VM List again
            break
        elif vm_name == vm['id']:
            vm_name = vm['name']
            os.system('virsh destroy %s' % vm_name)
            vm_exist = True
            vm_list = Utilities.get_vm_list()

    for name in vm_list['shutdown']:
        if vm_name == name:
            os.system('virsh undefine %s' % vm_name)
            vm_exist = True
            break

    if vm_exist:
        path = constant.vm_storage_path + vm_name + '.qcow2'
        print('deleting file : %s' % path)
        os.remove(path)
    else:
        raise Exception('VM %(vm_name)s is not exist!' % {'vm_name': vm_name})


def get_vm_status(vm_name):
    vm_list = Utilities.get_vm_list()

    for vm in vm_list['running']:
        if vm_name == vm['name'] or vm_name == vm['id']:
            return 'running'

    for name in vm_list['shutdown']:
        if vm_name == name:
            return 'shutdown'

    return None
