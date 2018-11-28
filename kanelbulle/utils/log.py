"""Utilities related to logging."""

import logging
from kanelbulle.config import config

# Log format to use.
FORMATTER = logging.Formatter('%(asctime)s | %(name)-10s | '
                              '%(levelname)-8s | %(message)s', '%Y-%m-%d '
                                                               '%H:%M:%S')

# Log levels to use.
LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}

# Associate each log level with a HTML color.
LOG_LEVEL_COLOR = {
    'CRITICAL': "purple",
    'ERROR': "red",
    'WARNING': "blue",
    'INFO': "black",
    'DEBUG': "green",
}

# Load configurations from file. If it fails, take predefined values.
ERROR = False
FILE_LEVEL = logging.DEBUG
CONSOLE_LEVEL = logging.WARNING

try:
    CONFIG = config.var.data['logger']
    FILE_LEVEL = LOG_LEVELS[CONFIG['file']['level'].upper()]
    CONSOLE_LEVEL = LOG_LEVELS[CONFIG['console']['level'].upper()]
except (TypeError, KeyError):
    ERROR = True

# Initialize handlers.
FILE = logging.FileHandler('kanelbulle/utils/log.log')
FILE.setFormatter(FORMATTER)
FILE.setLevel(FILE_LEVEL)

CONSOLE = logging.StreamHandler()
CONSOLE.setFormatter(FORMATTER)
CONSOLE.setLevel(CONSOLE_LEVEL)


def __init__():
    """Reset log file or create a new one in case the respective file does not
    exist.
    """
    wfile = logging.FileHandler('kanelbulle/utils/log.log', mode='w')
    wfile.setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(wfile)
    logger.info('Log file')
    logger.info(90*'-')


def get_logger(name):
    """Set up a new logger.

    Args:
        name: name of the new logger (string).

    Return:
        Logger with specified name.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(FILE)
    logger.addHandler(CONSOLE)

    return logger


# The different loggers used (alphabetical order).
app = get_logger('app')
config = get_logger('config')
log = get_logger('log')
gui = get_logger('gui')
socket = get_logger('socket')
