from Utils.Font import *


class ProfileParser:
    def __init__(self, profile):
        self.profile = profile

    def get_management_ip(self):
        if 'ip' in self.profile and 'Management' in self.profile['ip']:
            return self.profile['ip']['Management']['IP Address']

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


class smart_dict(dict):
    def __missing__(self, key):
        return None
