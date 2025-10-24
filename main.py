import time
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_datetime import datetime
from train_predictor import TrainPredictor
from time_conversion import TimeConversion
from display import Display

#xxx remove unused imports


# xxx doc The esp32-s3 comes with a co-processor for handling HTTP requests. So
# ideally we would send out the HTTP request to get updated arrival times and
# have the co-processor wait for the response. While we are waiting for the
# response the main processor can continue doing other tasks like animating the
# board. The idea here is that I could use async / await along with asyncio
# python library to do cooperative multitasking (
# https://learn.adafruit.com/cooperative-multitasking-in-circuitpython-with-asyncio/overview
# ). The main processor can just keep checking in to see if the co-processor has
# finished receiving the HTTP response. 
# 
# Unfortunately the CircuitPython Requests library that we can use for sending
# HTTP requests on the esp32-s3 Matrix Portal board does not have async method
# that we can use to send HTTP requests. There is an issue about this on GitHub,
# I did some investigation into this. It would be possible to add this
# functionality but it would be a lot of work because it would requiring making
# the low level socket using for sending the HTTP request async in order to add
# a way for the processor to wait for the coprocessor to receive response at the
# correct point in time. This is just too much work for the train board that I
# am working on.
# https://github.com/adafruit/Adafruit_CircuitPython_Requests/issues/134#issuecomment-3415845378 
# 
# xxx doc As a result we need to work around this issue. So we need to be
# careful about when we send the HTTP request so that it isn't in the middle of
# an animation or something.

DEBUG=True


# xxx doc
# xxx add more debugging
def print_debug(*args):
    if DEBUG:
        print(*args, sep="\n")


# xxx set the status led
matrixPortal = MatrixPortal(debug=DEBUG)
train_predictor = TrainPredictor(matrixPortal.network, datetime, datetime.now)
time_conversion = TimeConversion(datetime, datetime.now)
display = Display(matrixPortal, time_conversion, text_scroll_delay=0.1, train_frame_duration=0.1)


# xxx doc sync current time
# xxx is there any time float, I should probably update the time every once in a while.
matrixPortal.network.get_local_time(location="America/New_York")


last_check = None

trains = [None, None, None]
while True:
    if last_check is None or time.monotonic() > last_check + 180: #xxx check more frequently
        try:
            trains = train_predictor.next_trains(count = 3)
            last_check = time.monotonic()
        except (ValueError, RuntimeError) as e:
            print("Some error occured, retrying! -", e)
    
    if trains[0] is not None and time_conversion.time_is_soon(trains[0].time):
        display.render_train(trains[0].direction)
    else:
        display.render_arrival_times(trains)
        display.scroll_text()


