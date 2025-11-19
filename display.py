import time
import displayio
import gc
from train_predictor import Direction
from adafruit_progressbar.progressbar import HorizontalProgressBar

COUNTDOWN_TIMES_FONT='fonts/6x10.bdf'

class DisplayMode:
    NONE = 0
    COUNTDOWN = 1
    TRAIN = 2

class DisplayDependencies:
    def __init__(self,  matrix_portal, time_conversion, logger):
        self.matrix_portal = matrix_portal
        self.time_conversion = time_conversion
        self.logger = logger

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

    def initialize(self):
        self._initialize_train()
        self._initialize_countdown()
        gc.collect()

    def _set_mode(self, mode):
        if mode == DisplayMode.NONE:
            self._train_sprite_group.hidden = True

            self._countdown_progress_bar_group.hidden = True
            self._set_text_hidden(self._countdown_time_index, True)
        if mode == DisplayMode.COUNTDOWN:
            self._train_sprite_group.hidden = True

            self._countdown_progress_bar_group.hidden = False
            self._set_text_hidden(self._countdown_time_index, False)
        if mode == DisplayMode.TRAIN:
            self._train_sprite_group.hidden = False

            self._countdown_progress_bar_group.hidden = True
            self._set_text_hidden(self._countdown_time_index, True)

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

