from Utils.Font import *


class ProfileParser:
    def __init__(self, profile):
        self.profile = profile

    def get_management_ip(self):
        if 'ip' in self.profile and 'Management' in self.profile['ip']:
            return self.profile['ip']['Management']['IP Address']

    def get_control_ip(self):
        if 'ip' in self.profile and 'Control' in self.profile['ip']:
            return self.profile['ip']['Control']['IP Address']

    def get_cluster_ip(self):
        if 'ip' in self.profile and 'Cluster' in self.profile['ip']:
            return self.profile['ip']['Cluster']['IP Address']

    def set_management_ip(self, ip):
        if 'ip' in self.profile and 'Management' in self.profile['ip']:
            self.profile['ip']['Management']['IP Address'] = ip

    def set_control_ip(self, ip):
        if 'ip' in self.profile and 'Control' in self.profile['ip']:
            self.profile['ip']['Control']['IP Address'] = ip

    def set_cluster_ip(self, ip):
        if 'ip' in self.profile and 'Cluster' in self.profile['ip']:
            self.profile['ip']['Cluster']['IP Address'] = ip

    def set_ip(self, ip_type, ip):
        ip_type_map = {
            'management': self.set_management_ip,
            'control': self.set_control_ip,
            'controller': self.set_control_ip,
            'cluster': self.set_cluster_ip
        }
        ip_type_map[ip_type.lower()](ip)

    def get_branch(self):
        if 'branch' in self.profile:
            return self.profile['branch']

    def get_type(self):
        if 'type' in self.profile:
            return self.profile['type']

    def get_build(self):
        if 'build' in self.profile:
            return self.profile['build']

    def get_status(self):
        if 'status' in self.profile:
            return self.profile['status']

    def get_status_color_print(self):
        color_map = {
            'running': prGreen,
            'completed': prGreen,
            'downloading': prYellow,
            'setup': prYellow,
            'unmanaged': prYellow,
            'stopped': prPurple,
            'damaged': prRed,
            'stage1': prYellow,
        }

        if 'status' not in self.profile:
            return prNorm

        if self.profile['status'] not in color_map:
            return prNorm

        return color_map[self.profile['status']]

    def set_status(self, status):
        if 'status' in self.profile:
            self.profile['status'] = status


class smart_dict(dict):
    def __missing__(self, key):
        return None
