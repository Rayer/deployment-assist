from socket import *
import Utilities
import json
import Comm.CommConfig
from Comm import Cmds
__author__ = 'rayer'

if __name__ == '__main__':
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    cs.bind(('', Comm.CommConfig.proto_port))

    while True:
        (msg, b_from) = cs.recvfrom(4096)
        print('recv broadcast : %s' % msg)
        print(b_from)

        # Find if there is valid command in Cmds module
        eval_target = json.loads(msg).get('request') + '().handle_payload(json.loads(msg))'
        print(eval_target)
        ret = eval(eval_target)
        print(ret)
        cs.sendto(json.dumps(ret), b_from)
