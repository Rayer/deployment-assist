import Utilities
import sys
__author__ = 'rayer'

def get_cmd_list():
    pass


class GetVMList:

    def __init__(self):
        pass

    def broadcast_payload(self):
        return {} # No additional payload required

    @staticmethod
    def handle_payload(recv_payload=None):
        return Utilities.get_vm_list()


class GetVMStat:

    def __init__(self):
        pass

    def broadcast_payload(self):
        return {} # No additional payload required

    @staticmethod
    def handle_payload(recv_payload=None):
        return Utilities.get_vm_list()


class GetVMNameState:

    vm_name = ''
    def __init__(self, vm_name):
        self.vm_name

    def broadcast_payload(self):
        return {'vm_name': self.vm_name} # No additional payload required

    @staticmethod
    def handle_payload(recv_payload=None):
        return Utilities.get_vm_status(recv_payload['vm_name'])

