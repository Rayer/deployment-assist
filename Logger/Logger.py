import logging

from Utils.Singleton import singleton


@singleton
class Logger:
    def __init__(self):
        self.__logger__ = logging.getLogger(__name__)
        self.__loglevel__ = logging.DEBUG
        self.__format__ = 'LINE %(lineno)-4d : %(levelname)-8s %(message)s'
        self.__configuration__()

    def __configuration__(self):
        logging.basicConfig(level=self.__loglevel__, filename='/var/log/kvmdeployment.log',
                            format=self.__format__)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(self.__format__))
        self.get_logger().addHandler(console)

    def get_logger(self):
        return self.__logger__
