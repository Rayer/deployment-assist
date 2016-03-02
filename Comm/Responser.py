import json
import traceback
from socket import *

import Comm.Cmds
import Comm.CommConfig
from Logger.Logger import Logger

__author__ = 'rayer'


def responser_main():
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    cs.bind(('', Comm.CommConfig.proto_port))

    logger = Logger().get_logger()
    logger.info('Starting up Responser...')

    while True:
        (msg, b_from) = cs.recvfrom(4096)
        logger.info('recv broadcast : %s' % msg)
        print(b_from)

        try:
            # Find if there is valid command in Cmds module
            eval_target = json.loads(msg).get('request') + '.handle_payload(json.loads(msg))'
            logger.info(eval_target)
            ret = eval(eval_target)
            ret.update({'host': gethostname()})
            logger.info(ret)
            cs.sendto(json.dumps(ret), b_from)
        except BaseException as be:
            logger.error('Exception is caught!')
            logger.error(traceback.print_exc())


if __name__ == '__main__':
    responser_main()
