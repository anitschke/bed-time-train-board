# childrens-museum-franklin-train-board

xxx add background

xxx add animation of train here

xxx add recording of display

xxx you can press button to trigger train to go by. You must press and hold button until the train starts passing by.

xxx link to where you can see logs

## Maxtrix Portal Setup

### Flash with CircuitPython

The [instructions on setting up the Matrix Portal S3](https://learn.adafruit.com/adafruit-matrixportal-s3/install-circuitpython) that state you can just drag and drop the circuit python `.u2` file onto the `MATRXS3BOOT` drive don't seem to work correctly. However I was able to install it using the web installer on
* https://circuitpython.org/board/adafruit_matrixportal_s3/
* "Open Installer"
* "Install CircuitPython 10.0.0 UF2 Only"
* Continue following install instructions

Currently using `adafruit-circuitpython-matrixportal_m4-en_US-10.0.0`

### Install Adafruit Library

After setting up CircuitPython we need to install the Adafruit python libraries onto the device. This can be done by running the `install_circuitpython_lib.sh` script. This script installs EVERYTHING from that python bundle. There is a lot more than we need in that lib, but it is only 1MB so it isn't worth it to figure out what we do/don't need.

xxx actually now I cut down on the stuff there with 12639a794d5604a41d5e1b3bb21851ef8ebe4f4a but decided to revert because it was too complicated

### `settings.toml`

A `settings.toml` must be created inside this directory containing secrets and API keys. It will be copied over to the device when `install.sh` is run in the next step.

* `CIRCUITPY_WIFI_SSID` and `CIRCUITPY_WIFI_PASSWORD` need to contain the wifi SSID and password so the board can connect to wifi
* `CIRCUITPY_WEB_API_PORT` and `CIRCUITPY_WEB_API_PASSWORD` may be set to enable access to the board over wifi, this is generally not recommended for security reasons.
* `ADAFRUIT_AIO_USERNAME` and `ADAFRUIT_AIO_KEY` are required so it can push logs to the adafruit.io log feed and connect to the adafruit.io NTP time server so it can fetch the current time. A free account can be created at io.adafruit.com . xxx instructions on creating a feed
* `MBTA_API_KEY` xxx

xxx doc
```toml
CIRCUITPY_WIFI_SSID = "REDACTED"
CIRCUITPY_WIFI_PASSWORD = "REDACTED"

ADAFRUIT_AIO_USERNAME = "REDACTED"
ADAFRUIT_AIO_KEY      = "REDACTED"

MBTA_API_KEY = "REDACTED"
```
### Install the program

Run `install.sh` to install all of the 

## Running tests

xxx 

xxx setup GH action?

## Notes

### Implementation complexity

xxx doc add a note somewhere, maybe in the README that this is a lot more
complicated than it needs to be. If you just want simple text update without
the animation or other logic I need for computing and caching go point back at
an earlier commit.

### Computing arrival time offsets

xxx link to https://github.com/anitschke/childrens-museum-franklin-train-board-data-analysis

### Train sprite

xxx link to https://github.com/anitschke/childrens-museum-franklin-train-board-train-sprite

### dependency injection

xxx comments on how I am doing dependency injection and how that makes it easier to test

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

xxx doc at one point I set this up, see 12639a794d5604a41d5e1b3bb21851ef8ebe4f4a but it had issues where logging to the filesystem leads to the LEDs flasshing while we are writing to the file system. I am not sure why, I thought it might be a larger power draw to write to flash and used a better USB power supply but it still flashed. So IDK. I am also a little worried about wearing down the flash storage https://stackoverflow.com/questions/45982155/can-a-high-number-of-read-write-deteriorate-the-flash-itself so I reverted that change. 

xxx doc

Ideally I would also log with the RotatingFileHandler which provides very nice
rotating log files
https://github.com/adafruit/Adafruit_CircuitPython_Logging/blob/24c00a78a6ee6a41a87a8675e75742f990f1ee94/adafruit_logging.py#L325
There have been some cases where I have seen issues happen on the board but
haven't really sure why and without access to the logs it was difficult to
debug. Unfortunately CircuitPython currently only allows file system access either from the connected USB or 

it requires reconfiguring the device so we can't
write to it from the computer anymore.
https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage
I gave this a try and got an error

### Read Only Filesystem

xxx

https://github.com/adafruit/circuitpython/issues/9528#issuecomment-2293527157

xxx then reinstall

### Inspiration

xxx

https://jegamboafuentes.medium.com/i-created-my-own-subway-arrival-board-with-real-time-data-to-dont-miss-my-train-anymore-28bfded312c0

## References
* https://github.com/alejandrorascovan/mta-portal
* https://jegamboafuentes.medium.com/i-created-my-own-subway-arrival-board-with-real-time-data-to-dont-miss-my-train-anymore-28bfded312c0
* https://www.mbta.com/developers/v3-api
* https://github.com/jegamboafuentes/Train_schedule_board
* https://docs.circuitpython.org/projects/matrixportal/en/latest/

