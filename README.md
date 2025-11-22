# bed-time-train-board
I recently built a [train arrival board](https://github.com/anitschke/childrens-museum-franklin-train-board) for the [Children's Museum of Franklin](https://www.childrensmuseumfranklin.org/) to show when trains will pass by the window that they have that MBTA Franklin commuter rail line.

When it is time for our daughter to go to bed we often times pretend that their is a train coming and we ride the train upstairs to bed. So this is a fork of [`anitschke/childrens-museum-franklin-train-board`](https://github.com/anitschke/childrens-museum-franklin-train-board) that is a simplified version of the train arrival board that I made for the Children's Museum of Franklin that shows a countdown timer and plays a train animation when it is time to go to bed.

## Hardware

Adafruit makes it super easy to create an internet connected LED board like this. They sell a ESP32-S3 based board that integrates with HUB-75 based LED boards. Plug it in, write some python code, and just move it onto the board as if it was a USB drive.
* [Adafruit Matrix Portal S3 CircuitPython Powered Internet Display](https://www.adafruit.com/product/5778)
* [64x32 RGB LED Matrix - 6mm pitch](https://www.adafruit.com/product/2276)
* [TAP Plastics Chemcast Black LED Plastic Sheets](https://www.tapplastics.com/product/plastics/cut_to_size_plastic/black_led_sheet/668) - for on top of the LED board
* [Clear Adhesive Squares](https://www.adafruit.com/product/4813) - For attaching the acrylic sheet on top of the LEDs

## Maxtrix Portal Setup

### Flash with CircuitPython

The [instructions on setting up the Matrix Portal S3](https://learn.adafruit.com/adafruit-matrixportal-s3/install-circuitpython) that state you can just drag and drop the circuit python `.u2` file onto the `MATRXS3BOOT` drive don't seem to work correctly. However I was able to install it using the web installer on
* https://circuitpython.org/board/adafruit_matrixportal_s3/
* "Open Installer"
* "Install CircuitPython 10.0.0 UF2 Only"
* Continue following install instructions

Currently using `adafruit-circuitpython-matrixportal_m4-en_US-10.0.0`

### Install Adafruit Library

After setting up CircuitPython we need to install the Adafruit python libraries onto the device. This can be done by running the `install_circuitpython_lib.sh` script. This script installs EVERYTHING from that python bundle. There is a lot more than we need in that lib, but it is only 1MB so it isn't too bad to just include it all. At one pint I set up something to reduce the size and only install what I needed but the way I was doing it seemed to be fragile and I now that I am not logging to the file system I didn't need the extra space so decided to just get rid of that code. See [12639a7](https://github.com/anitschke/childrens-museum-franklin-train-board/commit/12639a794d5604a41d5e1b3bb21851ef8ebe4f4a).

### `settings.toml`

A `settings.toml` must be created inside this directory containing secrets and API keys. It will be copied over to the device when `install.sh` is run in the next step.

* `CIRCUITPY_WIFI_SSID` and `CIRCUITPY_WIFI_PASSWORD` need to contain the wifi SSID and password so the board can connect to wifi
* `CIRCUITPY_WEB_API_PORT` and `CIRCUITPY_WEB_API_PASSWORD` may be set to enable access to the board over wifi, this is generally not recommended for security reasons.
* `ADAFRUIT_AIO_USERNAME` and `ADAFRUIT_AIO_KEY` are required so it can push logs to the adafruit.io log feed and connect to the adafruit.io NTP time server so it can fetch the current time. A free account can be created at io.adafruit.com .

```toml
CIRCUITPY_WIFI_SSID = "REDACTED"
CIRCUITPY_WIFI_PASSWORD = "REDACTED"

ADAFRUIT_AIO_USERNAME = "REDACTED"
ADAFRUIT_AIO_KEY      = "REDACTED"
```

### Install the program

Run `install.sh` to install all of software and dependencies like the sprite sheet for the animation of the train onto the board.

## Notes

### Request a train

You can request that the train animation can play but holding down either the up or down buttons on the board when right when then "Children's Museum of Franklin" scrolling text disappears.

### Running tests

Unit tests can be run with Python by running the following at the root of the repository. Currently I am using Python 3.13.7 on Linux for testing.

```sh
python -m unittest discover -p "*_test.py"
```

### Debugging

You can connect to the board and view logs / get into the Python REPL shell using:

```
screen /dev/ttyACM0
```

* Note that sometimes the device name has a different digit after disconnecting / reconnecting (ex `/dev/ttyACM1`).

### Train sprite

I made a simple script using ImageMagick to help build a sprite sheet of a train animation to play when the train is about to pass by. The script for building this sprite sheet can be found in this GitHub Repo: https://github.com/anitschke/childrens-museum-franklin-train-board-train-sprite .

### Testing

### dependency injection

Rather than directly import Adafruit Python libraries many of the classes require that dependencies are passed into class contractors. This is primally to support testing. By avoiding directly import Adafruit Python libraries it allows for running tests with normal CPython by passing in mocks or normal Python versions of the classes. 

### `main.py` vs `code.py`

Most circuit python codebases seem to use `code.py` for the main entrypoint file, however circuit python also accept `main.py` as the main entrypoint file. We use `main.py` because VSCode test plugin hits the following error if we attempt to run tests and `code.py` exists. So we will just work around this and name the entry point file `main.py` instead.

```
Traceback (most recent call last):
  File "/home/anitschk/.vscode/extensions/ms-python.python-2025.16.0-linux-x64/python_files/unittestadapter/execution.py", line 24, in <module>
    from django_handler import django_execution_runner  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/anitschk/.vscode/extensions/ms-python.python-2025.16.0-linux-x64/python_files/unittestadapter/django_handler.py", line 15, in <module>
    from pvsc_utils import (  # noqa: E402
        VSCodeUnittestError,
    )
  File "/home/anitschk/.vscode/extensions/ms-python.python-2025.16.0-linux-x64/python_files/unittestadapter/pvsc_utils.py", line 6, in <module>
    import doctest
  File "/usr/lib/python3.13/doctest.py", line 101, in <module>
    import pdb
  File "/usr/lib/python3.13/pdb.py", line 77, in <module>
    import code
  File "/home/anitschk/sandbox/childrens-museum-franklin-train-board/code.py", line 4, in <module>
    import microcontroller
ModuleNotFoundError: No module named 'microcontroller'
Finished running tests!
```

### Logging to filesystem

At one point I set this up logging to the file system, see [12639a7](https://github.com/anitschke/childrens-museum-franklin-train-board/commit/12639a794d5604a41d5e1b3bb21851ef8ebe4f4a) but it had issues where logging to the filesystem leads to the LEDs flashing while writing to the file system. I am not sure why, I thought it might be a larger power draw to write to flash and used a better USB power supply but it still flashed. So IDK. I am also a little worried about wearing down the flash storage ( https://stackoverflow.com/questions/45982155/can-a-high-number-of-read-write-deteriorate-the-flash-itself ). It also adds a lot of extra complexity to the code so I reverted that change.

## References

* Supporting repos for this project:
  * Train animation sprites - https://github.com/anitschke/childrens-museum-franklin-train-board-train-sprite
  * Arrival time data analysis - https://github.com/anitschke/childrens-museum-franklin-train-board-data-analysis 
* Other train boards:
  * Enrique Gamboa's Medium article - https://jegamboafuentes.medium.com/i-created-my-own-subway-arrival-board-with-real-time-data-to-dont-miss-my-train-anymore-28bfded312c0
  * Enrique Gamboa's GitHub Repo - https://github.com/jegamboafuentes/Train_schedule_board
  * NYC MTA Train Arrival Board - https://github.com/alejandrorascovan/mta-portal
* Matrix Portal CircuitPython Documentation - https://docs.circuitpython.org/projects/matrixportal/en/latest/
* Matrix Portal Guide - https://learn.adafruit.com/adafruit-matrixportal-s3




