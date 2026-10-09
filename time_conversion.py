
class TimeConversion:        
    # format_relative_time_from_now converts a relative time in seconds. For
    # example "1min 25sec".
    def format_relative_time_from_now(self, time_seconds):

        if time_seconds <= 60:
            return f"{int(time_seconds)}sec"

        time_in_minutes, extra_seconds = divmod(time_seconds, 60.0)
        if extra_seconds == 0:
            return f"{int(time_in_minutes)}min"
        else:
            return f"{int(time_in_minutes)}min {int(extra_seconds)}sec"

    # format_clock_time formats hours (12-hour clock) and minutes.
    # For example 12:05 instead of 0:05 or 00:05.
    def format_clock_time(self, hour: int, minute: int) -> str:
        hour_12 = hour
        if hour_12 > 12:
            hour_12 -= 12
        elif hour_12 == 0:
            hour_12 = 12

        if hour_12 < 10:
            hour_str = f" {hour_12}"
        else:
            hour_str = f"{hour_12}"

        if minute < 10:
            minute_str = f"0{minute}"
        else:
            minute_str = f"{minute}"

        return f"{hour_str}:{minute_str}"

    def second_hand_angle(self, second: int) -> float:
        return second / 60 * 360

    def minute_hand_angle(self, minute: int) -> float:
        return minute / 60 * 360

    def hour_hand_angle(self, hour: int) -> float:
        return (hour % 12) / 12 * 360

    # analog_clock_angles calculates the angles (in degrees clockwise from noon)
    # for hour, minute, and second hands.
    def analog_clock_angles(self, hour: int, minute: int, second: int) -> tuple[float, float, float]:
        return (
            self.hour_hand_angle(hour),
            self.minute_hand_angle(minute),
            self.second_hand_angle(second),
        )