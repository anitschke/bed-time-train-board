
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