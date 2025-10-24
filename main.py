# xxx xxx xxx xxx This file is renamed to code.py.RENAMED_TO_FIX_TESTS because without this vscode errors out when trying to runtests because theere is some sort of module name collision or something. SO rennamed for now to fix this. Need to work around this. 

import time
import microcontroller
from board import NEOPIXEL
import displayio
import adafruit_display_text.label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_datetime import datetime, timedelta
import adafruit_ntp
import json
import gc
import displayio

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

ARRIVAL_TIMES_FONT='fonts/6x10.bdf'


#xxx doc
DATA_LOCATION = [
     ["times", 0],
     ["times", 1],
     ["times", 2]
]

#xxx doc
def print_debug(*args):
    if DEBUG:
        print(*args, sep="\n")


# xxx set the status led
matrixPortal = MatrixPortal(url=DATA_SOURCE, debug=DEBUG, json_path=DATA_LOCATION)

# xxx doc sync current time
# xxx is there any time float, I should probably update the time every once in a while.
matrixPortal.network.get_local_time(location="America/New_York")

# xxx doc
matrixPortal.network.add_json_transform(transform_json)

matrixPortal.set_background('/background.bmp')
matrixPortal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(15, 3), text="Children's Museum of Franklin", is_data=False, scrolling=True)

#xxx documentation seems to say that I can give a list of text_position but can't seem to get that to work, look into this some more
matrixPortal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(16, 11), text="?min", is_data=True)
matrixPortal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(16, 19), text="?min", is_data=True)
matrixPortal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(16, 27), text="?min", is_data=True)


last_check = None

while True:
    if last_check is None or time.monotonic() > last_check + 180: #xxx check more frequently
        try:
            value = matrixPortal.fetch()
            print_debug("Response is:", value)
            last_check = time.monotonic()
        except (ValueError, RuntimeError) as e:
            print("Some error occured, retrying! -", e)
    matrixPortal.scroll()
    time.sleep(0.03)


class DisplayMode:
    ARRIVAL_TIMES = 1
    TRAIN = 2

# xxx doc
# xxx test
class Display:
    def __init__(self, matrix_portal, text_scroll_delay, train_frame_duration):
        self._matrix_portal = matrix_portal
        self._mode = None
        self._text_scroll_delay = text_scroll_delay
        self._train_frame_duration = train_frame_duration
        
        self._arrival_time_indices = None
    
    def render_arrival_times(self, times):
        if self._mode != DisplayMode.ARRIVAL_TIMES:
            self._initialize_arrival_times()
        self._matrix_portal.set_text(times[0], self._arrival_time_indices[0])
        self._matrix_portal.set_text(times[1], self._arrival_time_indices[1])
        self._matrix_portal.set_text(times[2], self._arrival_time_indices[2])


    def _initialize_arrival_times(self):
        self._matrix_portal.remove_all_text()
        self._matrix_portal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(15, 3), text="Children's Museum of Franklin", is_data=False, scrolling=True)
        
        self._arrival_time_indices = [
            self._matrix_portal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(16, 11), text="?min", is_data=False),
            self._matrix_portal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(16, 19), text="?min", is_data=False),
            self._matrix_portal.add_text( text_font=ARRIVAL_TIMES_FONT, text_position=(16, 27), text="?min", is_data=False),
        ]
        self._mode = DisplayMode.ARRIVAL_TIMES

    def scroll_text(self):
        self._matrix_portal.scroll_text(self._text_scroll_delay)

    def render_train(self, direction):
        self._mode = DisplayMode.TRAIN
        self._render_train(direction)

        # After we have rendered the train replace the root group to make sure
        # we remove any existing train animation and then run the GC to free up
        # all the memory from the animation.
        self._matrix_portal.root_group = displayio.Group()
        gc.collect()
    
    def _render_train(self, direction):
        self._matrix_portal.remove_all_text()

        # Now that wae have removed all text replace the root group to make sure
        # there is nothing else being displayed.
        self._matrix_portal.root_group = displayio.Group()
        gc.collect()

        WIDTH=64
        HEIGHT=32

        matrix = Matrix(bit_depth=4)
        sprite_group = displayio.Group()
        matrix.display.root_group = sprite_group

        bitmap = displayio.OnDiskBitmap('/train.bmp')
        sprite = displayio.TileGrid(
            bitmap,
            pixel_shader=bitmap.pixel_shader,
            tile_width=WIDTH,
            tile_height=HEIGHT,
        )

        # The train animation is setup for an outbound train by default. So if
        # we want to render an inbound train we need to flip the sprite
        if (direction == Direction.IN_BOUND):
            sprite.flip_x = True

        self._matrix_portal.root_group.append(sprite)

        frame_count = int(bitmap.height / HEIGHT)
        current_frame = 0
        while True:
            time.sleep(self._train_frame_duration)
            current_frame = current_frame + 1
            if current_frame >= frame_count:
                return

            # Advance to the next frame by using __setitem__ on the
            # sprite_group.
            sprite_group[0][0] = current_frame