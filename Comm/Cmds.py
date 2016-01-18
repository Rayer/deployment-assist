import Utilities
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


class GetKVMHostStat:

    def __init__(self):
        pass

    def broadcast_payload(self):
        return {} # No additional payload required

    @staticmethod
    def handle_payload(recv_payload=None):
        return Utilities.get_host_stats()


class RequestSesame2:

    serial = ''

    def __init__(self, serial):
        self.serial = serial
        pass

    def broadcast_payload(self):
        return {'serial': self.serial}  # No additional payload required

    @staticmethod
    def handle_payload(recv_payload=None):
        return Utilities.get_sesame2(recv_payload['serial'])

