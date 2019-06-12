import os
import sys
from logging import DEBUG, INFO, Logger, StreamHandler, getLogger


def get_logger() -> Logger:
    log_level = 'INFO'
    _logger = getLogger('app')
    _logger.setLevel(log_level)

    stdout = StreamHandler(sys.stdout)
    # stdout.setFormatter()
    if os.getenv('DEBUG'):
        stdout.setLevel(DEBUG)
    else:
        stdout.setLevel(INFO)
    _logger.addHandler(stdout)

    return _logger


logger = get_logger()
