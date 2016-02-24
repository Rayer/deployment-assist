import json

'''
Sample profile format :
{"R-TestVSCG-ML":
    {"memory": 16, "memory_m": 16384, "force": false, "image_path": "",
    "ip":
        {"Control":
            {"IP Address": "10.2.5.248",
             "Netmask": "255.255.0.0",
             "Gateway": "no",
             "IP TYPE": "DHCP",
             "Control NAT IP": "Control NAT IP"},
         "Cluster":
            {"IP Address": "10.2.5.249",
             "Netmask": "255.255.0.0",
             "Gateway": "no",
             "IP TYPE": "DHCP"},
          "Management":
            {"IP Address": "172.17.60.137",
             "Netmask": "255.255.254.0",
             "Gateway": "yes",
             "IP TYPE": "DHCP"}},
    "stage1_only": false, "private": false, "name": "R-TestVSCG-ML",
    "ipv6": false, "type": "vscg", "build": "519", "branch": "ml",
    "nic": 3, "kernel_path": "", "cpu": 2, "interactive": true}}
'''

class DBAccess:
    def __enter__(self):
        self.__load__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__save__()

    def __init__(self):
        self.record = {}
        self.path = '/var/run/kvm.db'

    def __load__(self):
        with open(self.path, 'r+') as f:
            try:
                self.record = json.loads(f.read())
            except:
                print('no db found...')
                self.record = {}

    def __save__(self):
        with open(self.path, 'w+') as f:
            f.write(json.dumps(self.record))

    def create(self, profile):
        self.record.update({profile['name']: profile})

    def read(self, scg_name=None):
        if scg_name is None:
            return self.record.keys()

        if scg_name in self.record:
            return self.record[scg_name]

    def update(self, profile):
        self.create(profile)

    def delete(self, scg_name):
        if scg_name in self.record:
            del self.record[scg_name]


def open_scg_dao():
    return DBAccess()
