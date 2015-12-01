import zmq
import Comm.CommConfig
import time
import Utilities
import json
from socket import *
__author__ = 'rayer'

'''
This broadcaster do :
Periodically broadcast server status.
'''

if __name__ == '__main__':
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    cs.settimeout(1)
    # Send 'Who is Alive?' package
    payload_vm_status = '*__req_vm_stat %s' % '1B0291'
    who_is_alive = '*__req_alive %s' % '1B0291'

    while True:
        # payload = Utilities.get_vm_list()
        # payload['ip'] = '172.17.60.94'
        print('sending : %s' % who_is_alive)
        cs.sendto(json.dumps(who_is_alive), ('255.255.255.255', 11111))
        try:
            while True:
                recv, ipaddr = cs.recvfrom(4096)
                print('recv : %s' % recv)
        except BaseException as be:
            print(be)
            print('Timeout')
        time.sleep(10)

