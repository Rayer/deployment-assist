import Utilities


class GetVMList:

    def __init__(self):
        pass

    # Broadcast payload
    def broadcast_payload(self):
        return {} # No additional payload required

    # Handle while responser receive this
    def handle_payload(self, recv_payload=None):
        return Utilities.get_vm_list()

