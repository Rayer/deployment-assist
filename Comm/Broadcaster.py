import json
import time
from socket import *
from time import gmtime, strftime

import Cmds
from Comm.CommConfig import *

__author__ = 'rayer'

'''
This broadcaster do :
Periodically broadcast request, and responser will response request
'''


class Broadcaster:

    def_broadcast_addr = '172.17.61.255'
    def_buffersize = 4096
    def_timeout = 1

    def __init__(self, bind_port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.socket.settimeout(self.def_timeout)
        self.port = bind_port

    def broadcast_raw(self, raw_payload):
        ret = []
        # print('Sending : %s' % raw_payload)
        for broadcast_addr in broadcast_addr_list:
            self.socket.sendto(raw_payload, (broadcast_addr, self.port))

        try:
            while True:
                (recv, ipaddr) = self.socket.recvfrom(self.def_buffersize)
                # print('Receiving from : ' + ipaddr[0])
                ret.append((json.loads(recv),ipaddr))
        except BaseException as be:
            print(be)
            pass

        return ret

    def broadcast(self, broadcast_cmd):
        payload = {'request': broadcast_cmd.__module__ + '.' + broadcast_cmd.__class__.__name__,
                   'time': strftime("%Y-%m-%d %H:%M:%S", gmtime())}
        payload.update(broadcast_cmd.broadcast_payload())
        return self.broadcast_raw(json.dumps(payload))


if __name__ == '__main__':
    b = Broadcaster(proto_port)
    cmd = Cmds.GetVMList()
    while True:
        print(b.broadcast(cmd))
        time.sleep(10)

