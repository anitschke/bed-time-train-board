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
    def __init__(self, aio_handler, print_handler):
        self.aio_handler = aio_handler
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
    logger_level = min(log_levels.aio_handler, log_levels.print_handler)

    logger = logging.getLogger('')
    logger.setLevel(logger_level)

    aio_handler = AIOHandler(dependencies.matrix_portal, "cmf-train-board-logging", log_levels.aio_handler)
    logger.addHandler(aio_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_levels.print_handler)
    logger.addHandler(stream_handler)

    logger.debug("logging initialized")
    return logger

# AIOHandler logs to adafruit.io so I can easily monitor the board to be alerted if there are
# issues. 
class AIOHandler(logging.Handler):
    def __init__(self, matrix_portal, feed_name, level: int):
        super().__init__(level)
        self._feed_name = feed_name
        self._matrix_portal = matrix_portal

    def emit(self, record):
        try:
            self._matrix_portal.push_to_io(self._feed_name, self.format(record))
        except Exception as e:
            print(f"Failed to push logs to adafruit.io: ${e}")
