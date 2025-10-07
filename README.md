# childrens-museum-franklin-train-board





## Maxtrix Portal Setup

### Flash with CircuitPython

The [instructions on setting up the Matrix Portal S3](https://learn.adafruit.com/adafruit-matrixportal-s3/install-circuitpython) that state you can just drag and drop the circuit python `.u2` file onto the `MATRXS3BOOT` drive don't seem to work correctly. However I was able to install it using the web installer on
* https://circuitpython.org/board/adafruit_matrixportal_s3/
* "Open Installer"
* "Install CircuitPython 10.0.0 UF2 Only"
* Continue following install instructions

### Install Adafruit Library
Downloaded 10.x bundle from https://circuitpython.org/libraries and just installed entire `lib` directory from the bundle into the `lib` directory on the device. There is a lot more in that lib that we don't need but it is only 1MB so it isn't worth it to figure out what we do/don't need.

Documentation: https://docs.circuitpython.org/projects/matrixportal/en/latest/

