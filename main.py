import board
import digitalio
import wifi
import socketpool
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_datetime import datetime

import logging_extra
from time_conversion import TimeConversion
from display import Display, DisplayDependencies
from application import Application, ApplicationDependencies
from buttons import ButtonController
from webserver import create_webserver_controller

# 1. Initialize hardware matrix portal
matrix_portal = MatrixPortal(status_neopixel=board.NEOPIXEL)

# 2. Setup logging
log_levels = logging_extra.LogLevels(print_handler=logging_extra.DEBUG, aio_handler=logging_extra.INFO)
logger = logging_extra.newLogger(logging_extra.LoggerDependencies(matrix_portal), log_levels)

# 3. Setup hardware buttons
btn_down = digitalio.DigitalInOut(board.BUTTON_DOWN)
btn_down.switch_to_input(pull=digitalio.Pull.UP)
btn_up = digitalio.DigitalInOut(board.BUTTON_UP)
btn_up.switch_to_input(pull=digitalio.Pull.UP)

button_controller = ButtonController(
    is_button_down=lambda: not btn_down.value,
    is_button_up=lambda: not btn_up.value,
    default_countdown_seconds=5*60,
)

# 4. Setup web server controller
pool = socketpool.SocketPool(wifi.radio)
webserver_controller = create_webserver_controller(
    pool=pool,
    radio=wifi.radio,
    logger=logger,
    port=80,
    hostname="train",
)

controllers = [button_controller, webserver_controller]

# 5. Setup display
time_conversion = TimeConversion()
display = Display(DisplayDependencies(matrix_portal, time_conversion, logger), train_frame_duration=0.08)

# 6. Setup application
def sync_clock():
    matrix_portal.network.get_local_time(location="America/New_York")

app_deps = ApplicationDependencies(
    controllers=controllers,
    display=display,
    nowFcn=datetime.now,
    logger=logger,
    sync_clock_fcn=sync_clock,
)
app = Application(app_deps, default_countdown_seconds=5*60, train_render_count=5)

app.run()