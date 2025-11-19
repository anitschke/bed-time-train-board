import adafruit_logging as logging
import storage

__all__ = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "LogLevels",
    "LoggerDependencies",
    "newLogger",
]

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

class LoggerDependencies:
    def __init__(self,  matrix_portal):
        self.matrix_portal = matrix_portal
class LogLevels:
    def __init__(self, print_handler):
        self.print_handler = print_handler

# newLogger creates a new logger that logs to the serial bus / stdout and to
# adafruit.io so I can easily monitor the board to be alerted if there are
# issues. 
# 
# Ideally I would also log with the RotatingFileHandler which provides very nice
# rotating log files. I got it working but it ran into some issues and added a
# lot of extra complexity. For more details see "Logging to filesystem" in
# README.md
def newLogger( dependencies: LoggerDependencies, log_levels: LogLevels):

    # Set the log level of the logger to be the min of all the handlers so we
    # only log what the different handlers need. If we don't do this then the
    # log infrastructure will see that we don't have a handler at that lowest
    # level and will automatically log to a StreamHandler even if we don't want
    # that.
    #
    # logger_level = min(log_levels.print_handler)
    #
    # At the moment we only have one handler so just set it equal to the log
    # level for that handler.
    logger_level = log_levels.print_handler

    logger = logging.getLogger('')
    logger.setLevel(logger_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_levels.print_handler)
    logger.addHandler(stream_handler)

    logger.debug("logging initialized")
    return logger
