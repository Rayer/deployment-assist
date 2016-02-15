import logging

from Utils.Singleton import singleton


@singleton
class Logger:
    def __init__(self):
        self.__logger__ = logging.getLogger('kvm')
        self.__loglevel__ = logging.DEBUG
        logging.basicConfig(level=self.__loglevel__, filename='/var/log/kvmdeployment.log')

    def get_logger(self):
        return self.__logger__
