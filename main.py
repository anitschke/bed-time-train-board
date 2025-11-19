import os
import board

from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_datetime import datetime

import logging_extra
from time_conversion import TimeConversion
from display import Display, DisplayDependencies
from application import Application, ApplicationDependencies

matrix_portal = MatrixPortal(status_neopixel=board.NEOPIXEL)

log_levels = logging_extra.LogLevels(print_handler=logging_extra.DEBUG)
logger = logging_extra.newLogger(logging_extra.LoggerDependencies(matrix_portal), log_levels)

time_conversion = TimeConversion()
display = Display(DisplayDependencies(matrix_portal, time_conversion, logger), train_frame_duration=0.08)

app = Application(ApplicationDependencies(matrix_portal, display, datetime.now, logger), countdown_seconds=5*60, train_render_count=5)

app.run()