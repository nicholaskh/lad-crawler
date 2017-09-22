import logging


class LogUtil(object):

    @staticmethod
    def newLogger(name):
        return LogUtil(name)

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.name = name

    def info(self, message):
        #self.logger.info(message)
        print message

    def warning(self, message):
        #self.logger.warning(message)
        print message

    def error(self, message):
        #self.logger.error(message)
        print message

