import logging

from Utils.Singleton import singleton


@singleton
class Logger:
    def __init__(self):
        self.__logger__ = logging.getLogger(__name__)
        self.__loglevel__ = logging.DEBUG
        self.__format__ = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        self.__logfile__ = '/var/log/kvmdeployment.log'
        self.__configuration__()

    def __configuration__(self):
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(self.__format__))
        self.get_logger().addHandler(console)

        try:
            logging.basicConfig(level=self.__loglevel__, filename=self.__logfile__, format=self.__format__)
        except IOError:
            self.get_logger().warn('Can\'t open log file %s !' % self.__logfile__)

    def get_logger(self):
        return self.__logger__
