from commands import StartCountdownCommand

class ButtonController:
    """ButtonController polls hardware buttons and returns commands.
    
    Accepts button state probe functions (is_button_down, is_button_up) to enable
    unit testing in CPython without digitalio/board.
    """
    def __init__(self, is_button_down, is_button_up, default_countdown_seconds=300):
        self._is_button_down = is_button_down
        self._is_button_up = is_button_up
        self._default_countdown_seconds = default_countdown_seconds
        self._was_down_pressed = False
        self._was_up_pressed = False

    def poll(self) -> list:
        commands = []
        is_down = self._is_button_down()
        is_up = self._is_button_up()

        # Trigger command on transition (edge detection)
        down_edge = is_down and not self._was_down_pressed
        up_edge = is_up and not self._was_up_pressed

        if down_edge or up_edge:
            commands.append(StartCountdownCommand(self._default_countdown_seconds))

        self._was_down_pressed = is_down
        self._was_up_pressed = is_up
        return commands