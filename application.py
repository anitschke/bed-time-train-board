import time
import gc
from train_predictor import Direction
from commands import StartCountdownCommand, CancelCountdownCommand, PlayTrainNowCommand

class ApplicationDependencies:
    def __init__(self, controllers: list, display, nowFcn, logger, sync_clock_fcn=None, monotonic_fcn=time.monotonic):
        self.controllers = controllers
        self.display = display
        self.nowFcn = nowFcn
        self.logger = logger
        self.sync_clock_fcn = sync_clock_fcn
        self.monotonic_fcn = monotonic_fcn


class Application:
    def __init__(self, dependencies: ApplicationDependencies, default_countdown_seconds=5*60, train_render_count=5):
        self._controllers = dependencies.controllers
        self._display = dependencies.display
        self._nowFcn = dependencies.nowFcn
        self._logger = dependencies.logger
        self._sync_clock_fcn = dependencies.sync_clock_fcn
        self._monotonic_fcn = dependencies.monotonic_fcn

        self._default_countdown_seconds = default_countdown_seconds
        self._train_render_count = train_render_count

        self._countdown_start_time = None
        self._countdown_end_time = None

        self._last_nightly_tasks_run = self._monotonic_fcn()

    def run(self):
        self._startup()
        self._run_loop()

    def _startup(self):
        self._logger.info("starting train board")
        self._sync_clock()
        self._display.initialize()
        self._display.render_none()

    def _sync_clock(self):
        if self._sync_clock_fcn:
            self._logger.debug("getting network time")
            self._sync_clock_fcn()
            self._logger.debug(f"current time set to {self._nowFcn()}")

    def _nightly_tasks(self):
        # Make sure we only run the nightly tasks once a night
        now_mono = self._monotonic_fcn()
        if now_mono < self._last_nightly_tasks_run + 7200:
            return
        
        now = self._nowFcn()
        if now.hour != 3:
            return

        self._logger.debug("running nightly tasks")
        self._last_nightly_tasks_run = now_mono
        self._sync_clock()
        gc.collect()

    def _start_countdown(self, seconds: int):
        self._countdown_start_time = self._monotonic_fcn()
        self._countdown_end_time = self._countdown_start_time + seconds
        self._logger.info(f"Countdown started: {seconds}s")

    def _reset_countdown(self):
        self._countdown_start_time = None
        self._countdown_end_time = None

    def _cancel_countdown(self):
        self._logger.info("Countdown cancelled")
        self._reset_countdown()
        self._display.render_none()

    def _play_train(self):
        self._logger.info("Playing train")
        for _ in range(self._train_render_count):
            self._display.render_train(Direction.OUT_BOUND)
        self._reset_countdown()
        self._display.render_none()

    def _handle_command(self, command):
        if isinstance(command, StartCountdownCommand):
            duration = command.duration_seconds if command.duration_seconds else self._default_countdown_seconds
            self._start_countdown(duration)
        elif isinstance(command, CancelCountdownCommand):
            self._cancel_countdown()
        elif isinstance(command, PlayTrainNowCommand):
            self._play_train()
        else:
            self._logger.warning(f"Unknown command: {command}")

    def _poll_controllers(self):
        for controller in self._controllers:
            for command in controller.poll():
                self._handle_command(command)

    def run_iteration(self):
        """Executes a single step of the event loop. Publicly accessible for unit testing."""
        # First run nightly tasks
        self._nightly_tasks()

        # Poll controllers for user actions (buttons, web server, etc.)
        self._poll_controllers()

        # If no countdown is active, render clock
        if self._countdown_end_time is None:
            now = self._nowFcn()
            self._display.render_clock(now)
            return

        now_mono = self._monotonic_fcn()

        # If countdown expired, play train animation
        if now_mono > self._countdown_end_time:
            self._play_train()
            return

        # Render countdown progress bar and time remaining
        self._display.render_countdown(self._countdown_start_time, self._countdown_end_time, now_mono)

    def _run_loop(self):
        while True:
            self.run_iteration()
            # For some reason if we don't have any free cycles then the display
            # won't update. So we need to add a short sleep to give some cycles
            # for it to update the display.
            time.sleep(0.1)

