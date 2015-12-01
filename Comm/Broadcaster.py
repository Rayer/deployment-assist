import zmq
import Comm.CommConfig
import time
from BC_Cmds.GetVMList import GetVMList
import json
from socket import *
__author__ = 'rayer'

'''
This broadcaster do :
Periodically broadcast request, and responser will response request
'''


class Broadcaster:

    def_broadcast_addr = '10.2.255.255'
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
        print('Sending : %s' % raw_payload)
        self.socket.sendto(raw_payload, (self.def_broadcast_addr, self.port))
        try:
            while True:
                (recv, ipaddr) = self.socket.recvfrom(self.def_buffersize)
                print('Receiving from : ' + ipaddr[0])
                ret.append((recv,ipaddr))
        except BaseException as be:
            print(be)

        return ret

    def broadcast(self, broadcast_cmd):
        payload = {'request': broadcast_cmd.__class__.__name__}
        payload.update(broadcast_cmd.broadcast_payload())
        return self.broadcast_raw(json.dumps(payload))


if __name__ == '__main__':
    b = Broadcaster(Comm.CommConfig.proto_port)
    # payload = '*__req_addr_ '
    cmd = GetVMList()
    while True:
        print(b.broadcast(cmd))
        time.sleep(10)

