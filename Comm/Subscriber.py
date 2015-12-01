from socket import *
import Utilities
import json
import Comm.CommConfig
__author__ = 'rayer'

if __name__ == '__main__':
    cs = socket(AF_INET, SOCK_DGRAM)
    # cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    cs.bind(('', Comm.CommConfig.proto_port))

    while True:
        (msg, b_from) = cs.recvfrom(4096)
        print('recv broadcast : %s' % msg)
        print(b_from)
        payload = json.dumps(Utilities.get_vm_list())
        print(payload)
        cs.sendto(payload, b_from)
