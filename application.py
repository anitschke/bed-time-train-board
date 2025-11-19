import time
from train_predictor import Direction
from buttons import button_down_depressed, button_up_depressed
from train_predictor import Direction

NUM_TRAINS_TO_FETCH=3
class ApplicationDependencies:
    def __init__(self, matrix_portal, display, nowFcn, logger):
        self.matrix_portal  = matrix_portal 
        self.display = display
        self.nowFcn = nowFcn
        self.logger = logger

class Application:
    def __init__(self, dependencies: ApplicationDependencies, countdown_seconds, train_render_count ):
        self._matrix_portal  = dependencies.matrix_portal 
        self._display = dependencies.display
        self._nowFcn = dependencies.nowFcn
        self._logger = dependencies.logger

        self._last_nightly_tasks_run = time.monotonic()
        self._countdown_seconds = countdown_seconds

        self._train_render_count = train_render_count

        self._countdown_end_time = None
        self._countdown_start_time = None

    def run(self):
        self._startup()
        self._run_loop()

    def _startup(self):
        self._logger.info("starting train board")
        self._display.initialize()
        self._display.render_none()

    def _reset_countdown(self):
        self._countdown_start_time = None
        self._countdown_end_time = None

    def _start_countdown(self):
        self._countdown_start_time = time.monotonic()
        self._countdown_end_time = self._countdown_start_time + self._countdown_seconds
            
    def _run_loop(self):
        while True:
            # First look for user input from buttons.
            # 
            # Note ideally we would use something like hardware interrupts or
            # asyncio to monitor button presses but this adds a lot of
            # complexity to the code so instead we will just check the current
            # state of the button at this point in time. This means that you
            # must be pressing the button when we check for the button press or
            # else the press won't be registered.
            if button_up_depressed():
                self._start_countdown()
                continue
            if button_down_depressed():
                self._start_countdown()
                continue              
            
            # No countdown, just keep checking buttons
            if self._countdown_end_time is None:
                continue

            now = time.monotonic()

            # Check if we need to play the train because countdown finished
            if now > self._countdown_end_time:
                for _ in range(self._train_render_count):
                    self._display.render_train(Direction.OUT_BOUND)
                self._reset_countdown()
                self._display.render_none()
                continue

            # Display countdown
            self._display.render_countdown(self._countdown_start_time, self._countdown_end_time, now)
            
            # For some reason if we don't have any free cycles then the display
            # won't update. So we need to add a short sleep to give some cycles
            # for it to update the display.
            time.sleep(0.1)
            


