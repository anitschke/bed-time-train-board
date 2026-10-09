import unittest
from datetime import datetime
from commands import StartCountdownCommand, CancelCountdownCommand, PlayTrainNowCommand
from application import Application, ApplicationDependencies
from train_predictor import Direction

class MockLogger:
    def info(self, msg): pass
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


class MockDisplay:
    def __init__(self):
        self.initialized = False
        self.rendered_none = 0
        self.rendered_clocks = []
        self.rendered_countdowns = []
        self.rendered_trains = []

    def initialize(self):
        self.initialized = True

    def render_none(self):
        self.rendered_none += 1

    def render_clock(self, now):
        self.rendered_clocks.append(now)

    def render_countdown(self, start, end, current):
        self.rendered_countdowns.append((start, end, current))

    def render_train(self, direction):
        self.rendered_trains.append(direction)


class MockController:
    def __init__(self):
        self.commands = []

    def poll(self):
        cmds = self.commands
        self.commands = []
        return cmds


class TestApplication(unittest.TestCase):
    def setUp(self):
        self.mock_controller = MockController()
        self.mock_display = MockDisplay()
        self.mock_logger = MockLogger()
        self.clock_synced = False

        def sync_clock():
            self.clock_synced = True

        self.fixed_now = datetime(2026, 10, 8, 20, 0, 0)
        self.deps = ApplicationDependencies(
            controllers=[self.mock_controller],
            display=self.mock_display,
            nowFcn=lambda: self.fixed_now,
            logger=self.mock_logger,
            sync_clock_fcn=sync_clock,
        )
        self.app = Application(self.deps, default_countdown_seconds=300, train_render_count=3)

    def test_startup(self):
        self.app._startup()
        self.assertTrue(self.clock_synced)
        self.assertTrue(self.mock_display.initialized)
        self.assertEqual(self.mock_display.rendered_none, 1)

    def test_handle_start_countdown_command(self):
        # Inject controllable monotonic clock
        current_mono = 1000.0
        self.app._monotonic_fcn = lambda: current_mono

        # Send command to start a 120s countdown
        cmd = StartCountdownCommand(duration_seconds=120)
        self.mock_controller.commands = [cmd]

        # First iteration: polls command, starts countdown, renders countdown
        self.app.run_iteration()
        self.assertEqual(self.app._countdown_start_time, 1000.0)
        self.assertEqual(self.app._countdown_end_time, 1120.0)
        self.assertEqual(len(self.mock_display.rendered_countdowns), 1)
        self.assertEqual(len(self.mock_display.rendered_trains), 0)

        # Advance time by 60s (halfway)
        current_mono = 1060.0
        self.app.run_iteration()
        self.assertEqual(len(self.mock_display.rendered_countdowns), 2)
        self.assertEqual(len(self.mock_display.rendered_trains), 0)

        # Advance time past countdown end (121s elapsed)
        current_mono = 1121.0
        # train_render_count is 3, each iteration renders one train pass
        self.app.run_iteration()
        self.assertEqual(len(self.mock_display.rendered_trains), 1)
        self.assertEqual(self.app._remaining_trains, 2)
        self.assertIsNone(self.app._countdown_end_time)

        self.app.run_iteration()
        self.assertEqual(len(self.mock_display.rendered_trains), 2)
        self.assertEqual(self.app._remaining_trains, 1)

        self.app.run_iteration()
        self.assertEqual(len(self.mock_display.rendered_trains), 3)
        self.assertEqual(self.app._remaining_trains, 0)
        self.assertGreaterEqual(self.mock_display.rendered_none, 1)

        # Next iteration: reverts to rendering regular clock
        self.app.run_iteration()
        self.assertEqual(len(self.mock_display.rendered_clocks), 1)

    def test_handle_cancel_countdown_command(self):
        self.app._handle_command(StartCountdownCommand(duration_seconds=120))
        self.assertIsNotNone(self.app._countdown_end_time)

        self.app._handle_command(CancelCountdownCommand())
        self.assertIsNone(self.app._countdown_start_time)
        self.assertIsNone(self.app._countdown_end_time)
        self.assertEqual(self.app._remaining_trains, 0)
        self.assertEqual(self.mock_display.rendered_none, 1)

    def test_handle_play_train_now_command(self):
        self.app._handle_command(StartCountdownCommand(duration_seconds=120))
        self.app._handle_command(PlayTrainNowCommand())

        self.assertEqual(self.app._remaining_trains, 3)
        self.assertIsNone(self.app._countdown_end_time)

        for i in range(1, 4):
            self.app.run_iteration()
            self.assertEqual(len(self.mock_display.rendered_trains), i)

        self.assertEqual(self.app._remaining_trains, 0)
        self.assertEqual(self.mock_display.rendered_none, 1)

    def test_cancel_train_while_playing(self):
        # Trigger train animation (3 loops)
        self.app._handle_command(PlayTrainNowCommand())
        self.assertEqual(self.app._remaining_trains, 3)

        # Play 1 loop of train
        self.app.run_iteration()
        self.assertEqual(len(self.mock_display.rendered_trains), 1)
        self.assertEqual(self.app._remaining_trains, 2)

        # Cancel while train is playing
        self.mock_controller.commands = [CancelCountdownCommand()]
        self.app.run_iteration()

        # Remaining trains should be reset to 0, no more trains rendered, and reverted to clock
        self.assertEqual(self.app._remaining_trains, 0)
        self.assertEqual(len(self.mock_display.rendered_trains), 1)
        self.assertEqual(len(self.mock_display.rendered_clocks), 1)

        # Subsequent iteration continues rendering clock
        self.app.run_iteration()
        self.assertEqual(len(self.mock_display.rendered_clocks), 2)

    def test_poll_controllers(self):
        self.mock_controller.commands = [StartCountdownCommand(duration_seconds=600)]
        self.app._poll_controllers()
        self.assertIsNotNone(self.app._countdown_end_time)


if __name__ == '__main__':
    unittest.main()
