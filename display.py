import time
import displayio
import math
import gc
from train_predictor import Direction
from adafruit_progressbar.progressbar import HorizontalProgressBar
from adafruit_display_shapes.circle import Circle 
from adafruit_display_shapes.polygon import Polygon 


COUNTDOWN_TIMES_FONT='fonts/6x10.bdf'
DIGITAL_CLOCK_FONT='fonts/6x10.bdf'
ANALOG_CLOCK_FONT='fonts/4x6.bdf'

class DisplayMode:
    NONE = 0
    COUNTDOWN = 1
    TRAIN = 2
    CLOCK = 3

class DisplayDependencies:
    def __init__(self,  matrix_portal, time_conversion, logger):
        self.matrix_portal = matrix_portal
        self.time_conversion = time_conversion
        self.logger = logger

class ClockHand(displayio.TileGrid):
    def __init__(
        self,
        l: int,
        color: int,
        x0: int=16,
        y0: int=16,
    ):
        
        self._x0 = x0
        self._y0 = y0
        self._l = l

        self._palette = displayio.Palette(2)
        self._palette.make_transparent(0)
        self._palette[1] = color
        self._bitmap = displayio.Bitmap(64, 32, 2)

        self._angle = 0

        super().__init__(self._bitmap, pixel_shader=self._palette, x=0, y=0)


    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, angle: float):
        # angle in degrees clockwise from noon.

        # Prevent flashing of hands and only redraw if the angle has changed
        if not self._angle == angle:
            self._angle = angle
            self._draw()

    def _draw(self):
        # A key thing to remember when thinking about these angles is that this
        # that positive y points DOWN and not up like it would when normally
        # thinking about cartesian coordinates. This means that a positive
        # rotation is in the clockwise direction and not the anti clockwise
        # direction. Since we want a zero angle to like up with 12 o'clock all
        # we need to do is subtract 90 degrees to rotate zero degrees around to
        # be at 12 o'clock.
        angle_rad = math.radians(self._angle - 90)
        x = int(self._l * math.cos(angle_rad) + self._x0)
        y = int(self._l * math.sin(angle_rad) + self._y0)

        colorIdx = 1
        self._bitmap.fill(0)
        Polygon.draw(self._bitmap, [(self._x0, self._y0), (x, y)], colorIdx, close=False)


# Display is the class for interacting with the LED board do so things like
# display the arrival times and the train animation when the train gets close
# by.
class Display:
    def __init__(self, dependencies : DisplayDependencies, train_frame_duration):
        self._matrix_portal = dependencies.matrix_portal
        self._time_conversion = dependencies.time_conversion
        self._logger = dependencies.logger

        self._mode = None
        self._train_frame_duration = train_frame_duration

        self._timeStr = None

    def initialize(self):
        self._initialize_train()
        self._initialize_countdown()
        self._initialize_clock()
        gc.collect()

    def _set_mode(self, mode):
        if mode == DisplayMode.NONE:
            self._train_sprite_group.hidden = True

            self._countdown_progress_bar_group.hidden = True
            self._set_text_hidden(self._countdown_time_index, True)

            self._analog_clock_group.hidden = True
            self._set_text_hidden(self._digital_clock_index, True)
            self._set_text_hidden(self._analog_clock_index_12, True)
            self._set_text_hidden(self._analog_clock_index_3, True)
            self._set_text_hidden(self._analog_clock_index_6, True)
            self._set_text_hidden(self._analog_clock_index_9, True)
        if mode == DisplayMode.COUNTDOWN:
            self._train_sprite_group.hidden = True

            self._countdown_progress_bar_group.hidden = False
            self._set_text_hidden(self._countdown_time_index, False)

            self._analog_clock_group.hidden = True
            self._set_text_hidden(self._digital_clock_index, True)
            self._set_text_hidden(self._analog_clock_index_12, True)
            self._set_text_hidden(self._analog_clock_index_3, True)
            self._set_text_hidden(self._analog_clock_index_6, True)
            self._set_text_hidden(self._analog_clock_index_9, True)
        if mode == DisplayMode.TRAIN:
            self._train_sprite_group.hidden = False

            self._countdown_progress_bar_group.hidden = True
            self._set_text_hidden(self._countdown_time_index, True)

            self._analog_clock_group.hidden = True
            self._set_text_hidden(self._digital_clock_index, True)
            self._set_text_hidden(self._analog_clock_index_12, True)
            self._set_text_hidden(self._analog_clock_index_3, True)
            self._set_text_hidden(self._analog_clock_index_6, True)
            self._set_text_hidden(self._analog_clock_index_9, True)
        if mode == DisplayMode.CLOCK:
            self._train_sprite_group.hidden = True

            self._countdown_progress_bar_group.hidden = True
            self._set_text_hidden(self._countdown_time_index, True)
            
            self._analog_clock_group.hidden = False
            self._set_text_hidden(self._digital_clock_index, False)
            self._set_text_hidden(self._analog_clock_index_12, False)
            self._set_text_hidden(self._analog_clock_index_3, False)
            self._set_text_hidden(self._analog_clock_index_6, False)
            self._set_text_hidden(self._analog_clock_index_9, False)


        self._mode = mode

    def _set_text_hidden(self, text_index:int, hidden:bool):
        self._matrix_portal.text_fields[text_index].get("label").hidden = hidden

    def _initialize_train(self):
        self._logger.debug("initializing train")
        WIDTH=64
        HEIGHT=32

        bitmap = displayio.OnDiskBitmap('/train.bmp')
        self._train_sprite = displayio.TileGrid(
            bitmap,
            pixel_shader=bitmap.pixel_shader,
            tile_width=WIDTH,
            tile_height=HEIGHT,
        )

        self._train_sprite_group = displayio.Group()
        self._train_sprite_group.append(self._train_sprite)
        self._matrix_portal.display.root_group.append(self._train_sprite_group)

        self._train_frame_count = int(bitmap.height / HEIGHT)

    def _initialize_clock(self):

        self._analog_clock_outline = Circle(x0=16, y0=16, r=15, outline=0x0000DD, stroke=1)
        self._analog_clock_second = ClockHand(l=14, color=0xFF0000)
        self._analog_clock_minute = ClockHand(l=10, color=0x00FF00)
        self._analog_clock_hour = ClockHand(l=5, color=0x0000FF)

        # We need to append the elements in this order to ensure that the
        # shorter hands render on top of the longer hands so they are always
        # visible.
        self._analog_clock_group = displayio.Group()
        self._analog_clock_group.append(self._analog_clock_outline)
        self._analog_clock_group.append(self._analog_clock_second)
        self._analog_clock_group.append(self._analog_clock_minute)
        self._analog_clock_group.append(self._analog_clock_hour)

        self._matrix_portal.display.root_group.append(self._analog_clock_group)

        self._digital_clock_index = self._matrix_portal.add_text( text_font=DIGITAL_CLOCK_FONT, text_position=(34, 16), text_anchor_point=(0, 0.5), text="?", is_data=False)

        self._analog_clock_index_12 = self._matrix_portal.add_text( text_font=ANALOG_CLOCK_FONT, text_position=(17, 4), text_anchor_point=(0.5, 0.5), text="12", is_data=False)
        self._analog_clock_index_3 = self._matrix_portal.add_text( text_font=ANALOG_CLOCK_FONT, text_position=(30, 16), text_anchor_point=(0.5, 0.5), text="3", is_data=False)
        self._analog_clock_index_6 = self._matrix_portal.add_text( text_font=ANALOG_CLOCK_FONT, text_position=(17, 28), text_anchor_point=(0.5, 0.5), text="6", is_data=False)
        self._analog_clock_index_9 = self._matrix_portal.add_text( text_font=ANALOG_CLOCK_FONT, text_position=(4, 16), text_anchor_point=(0.5, 0.5), text="9", is_data=False)



    def render_clock(self, now: datetime):
        self._set_mode(DisplayMode.CLOCK)

        self._analog_clock_second.angle = now.second / 60 * 360
        self._analog_clock_minute.angle = now.minute / 60 * 360
        self._analog_clock_hour.angle = now.hour / 12 * 360

        hour = now.hour % 12
        if hour < 10:
            hourStr = f" {hour}"
        else:
            hourStr = f"{hour}"

        if now.minute < 10:
            minuteStr = f"0{now.minute}"
        else:
            minuteStr = f"{now.minute}"

        # prevent flashing of numbers and only update if the time string has
        # actually changed.
        timeStr = f"{hourStr}:{minuteStr}"
        if not timeStr == self._timeStr:
            self._timeStr = timeStr
            self._matrix_portal.set_text(timeStr, self._digital_clock_index)

    def render_none(self):
        self._set_mode(DisplayMode.NONE)

    def render_train(self, direction):
        self._logger.debug("rendering train")
        self._set_mode(DisplayMode.TRAIN)

        # The train animation is setup for an outbound train by default. So if
        # we want to render an inbound train we need to flip the sprite.
        # Otherwise we need to make sure we DON'T flip the sprit (it might have
        # been set to flip_x from last time we rendered a train).
        self._train_sprite.flip_x = direction == Direction.IN_BOUND

        current_frame = 0
        while True:
            time.sleep(self._train_frame_duration)
            current_frame = current_frame + 1
            if current_frame >= self._train_frame_count:
                return

            # Advance to the next frame by using __setitem__ on the
            # sprite_group.
            self._train_sprite_group[0][0] = current_frame

    def _initialize_countdown(self):
        self._logger.debug("initializing countdown")
        self._countdown_progress_bar = HorizontalProgressBar(
            position=(0, 0),
            size=(64, 15),
            bar_color=0xFF0000,
            outline_color=0x00FF00,
            fill_color=0x0000FF,
            min_value=0,
            max_value=1,
        )
        self._countdown_progress_bar_group = displayio.Group()
        self._matrix_portal.display.root_group.append(self._countdown_progress_bar_group)
        self._countdown_progress_bar_group.append(self._countdown_progress_bar)

        self._countdown_time_index = self._matrix_portal.add_text( text_font=COUNTDOWN_TIMES_FONT, text_position=(32, 24), text_anchor_point=(0.5, 0.5), text="?", is_data=False)

    def render_countdown(self, start_time_seconds, end_time_seconds, current_time_seconds):
        self._set_mode(DisplayMode.COUNTDOWN)

        total_seconds = end_time_seconds-start_time_seconds
        remaining_seconds = end_time_seconds-current_time_seconds
        ratio = remaining_seconds / total_seconds

        # self._countdown_progress_bar.value asserts if value is greater than 1.
        if ratio > 1:
            ratio = 1

        self._countdown_progress_bar.value = ratio

        display_time = self._time_conversion.format_relative_time_from_now(remaining_seconds)

        # If we set it every cycle then the display jitters for some reason. So
        # only update the value if it has actually changed.
        if not self._matrix_portal.text_fields[self._countdown_time_index]["label"].text == display_time:
            self._matrix_portal.set_text(display_time, self._countdown_time_index)

