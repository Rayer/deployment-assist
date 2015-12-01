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


class Broadcaster:

    def_broadcast_addr = '255.255.255.255'
    def_buffersize = 4096
    def_timeout = 1

    def __init__(self, bind_port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.socket.settimeout(self.def_timeout)
        self.port = bind_port

    def broadcast(self, payload):
        ret = []
        self.socket.sendto(payload, (self.def_broadcast_addr, self.port))
        try:
            while True:
                (recv, ipaddr) = self.socket.recvfrom(self.def_buffersize)
                print('Receiving from : ' + ipaddr[0])
                ret.append((recv,ipaddr))
        except BaseException as be:
            print(be)

        return ret


if __name__ == '__main__':
    b = Broadcaster(Comm.CommConfig.proto_port)
    payload = '*__req_addr_ '
    while True:
        print(b.broadcast(payload))
        time.sleep(10)

