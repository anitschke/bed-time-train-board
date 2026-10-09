class StartCountdownCommand:
    def __init__(self, duration_seconds: int):
        self.duration_seconds = duration_seconds

    def __repr__(self):
        return f"StartCountdownCommand(duration_seconds={self.duration_seconds})"

    def __eq__(self, other):
        return isinstance(other, StartCountdownCommand) and self.duration_seconds == other.duration_seconds


class CancelCountdownCommand:
    def __repr__(self):
        return "CancelCountdownCommand()"

    def __eq__(self, other):
        return isinstance(other, CancelCountdownCommand)


class PlayTrainNowCommand:
    def __repr__(self):
        return "PlayTrainNowCommand()"

    def __eq__(self, other):
        return isinstance(other, PlayTrainNowCommand)
