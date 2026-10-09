import unittest
from buttons import ButtonController
from commands import StartCountdownCommand

class TestButtonController(unittest.TestCase):
    def test_no_press_returns_no_commands(self):
        controller = ButtonController(is_button_down=lambda: False, is_button_up=lambda: False, default_countdown_seconds=300)
        self.assertEqual(controller.poll(), [])

    def test_button_down_press_triggers_countdown(self):
        is_down = False
        controller = ButtonController(is_button_down=lambda: is_down, is_button_up=lambda: False, default_countdown_seconds=300)
        
        self.assertEqual(controller.poll(), [])

        # Press down button
        is_down = True
        commands = controller.poll()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], StartCountdownCommand(300))

        # Holding button does not trigger again (edge detection)
        self.assertEqual(controller.poll(), [])

        # Release button
        is_down = False
        self.assertEqual(controller.poll(), [])

        # Press again triggers new command
        is_down = True
        commands2 = controller.poll()
        self.assertEqual(len(commands2), 1)
        self.assertEqual(commands2[0], StartCountdownCommand(300))

    def test_button_up_press_triggers_countdown(self):
        is_up = False
        controller = ButtonController(is_button_down=lambda: False, is_button_up=lambda: is_up, default_countdown_seconds=120)
        
        is_up = True
        commands = controller.poll()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], StartCountdownCommand(120))


if __name__ == '__main__':
    unittest.main()
