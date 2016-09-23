import json
from socket import *
from time import gmtime, strftime

from Comm.CommConfig import *
from Logger.Logger import Logger

__author__ = 'rayer'

'''
This broadcaster do :
Periodically broadcast request, and responser will response request
'''


class Broadcaster:
    def_buffersize = 512 * 1024

    def __init__(self, bind_port=proto_port, broadcast_ip=None):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.socket.settimeout(broadcast_timeout)
        self.port = bind_port
        self.brocast_ip_list = broadcast_ip if broadcast_ip is not None else broadcast_addr_list
        logger = Logger().get_logger()
        logger.info('Starting up Broadcaster...')


    def broadcast_raw(self, raw_payload):
        logger = Logger().get_logger()
        ret = []
        logger.info('Sending : %s' % raw_payload)
        for broadcast_addr in self.brocast_ip_list:
            logger.debug('Sending to %s' % broadcast_addr)
            self.socket.sendto(raw_payload, (broadcast_addr, self.port))

        try:
            while True:
                (recv, ipaddr) = self.socket.recvfrom(self.def_buffersize)
                logger.info('Receiving from : ' + ipaddr[0])
                ret.append((json.loads(recv), ipaddr))
        except BaseException as be:
            # logger.error(be)
            logger.info('time out')

        logger.debug('Get ret : %s' % ret)
        return ret

    def broadcast(self, broadcast_cmd):
        payload = {'request': broadcast_cmd.__module__ + '.' + broadcast_cmd.__class__.__name__,
                   'time': strftime("%Y-%m-%d %H:%M:%S", gmtime())}
        payload.update(broadcast_cmd.broadcast_payload())
        return self.broadcast_raw(json.dumps(payload))
