import logging

from __about__ import PROJECT_NAME

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'


def get_logger_with_adapter(logger, uid: str):
    return MyLoggerAdapter(logger, {'uid': uid})

class MyLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        message = ' - '.join((self.extra['uid'], str(msg)))
        return message, kwargs


def get_logger(name: str = None):
    logger = logging.getLogger(name or PROJECT_NAME)

    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel('INFO')
    formatter = logging.Formatter(LOG_FORMAT)
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger
