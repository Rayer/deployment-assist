import Logger
from Logger.Logger import Logger
from Utils.Singleton import Singleton


class SanityTestModule:
    def __init__(self):
        SanityTest().register_module(self)

    def __mark_as_failed__(self):
        pass

    def __mark_checkpoint__(self):
        pass

    def log_text(self, text):
        content = SanityTest.get_content()
        content += '[{}]'.format(self.__class__)
        content += text
        content += '\r'


@Singleton
class SanityTest:
    registered_module_map = {}
    content = ''

    def __init__(self):
        self.logger = Logger().get_logger()
        self.logger.log('Sanity Test Initialized')

    def register_module(self, module):
        self.registered_module_map.update({module.__class__: module})
        self.logger.log('Module {} registered'.format(module.__class__))

    def get_content(self):
        return self.content
