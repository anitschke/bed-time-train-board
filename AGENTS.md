# AGENTS.md

Welcome! This document provides technical context, architecture guidelines, development conventions, and operational workflows for AI agents and human contributors working on `bed-time-train-board`.

---

## 1. Project Overview & Architecture

`bed-time-train-board` is a CircuitPython application designed to run on the [Adafruit MatrixPortal S3](https://www.adafruit.com/product/5778) driving a 64x32 RGB HUB-75 LED matrix. It is a streamlined fork of [`anitschke/childrens-museum-franklin-train-board`](https://github.com/anitschke/childrens-museum-franklin-train-board).

Its primary functions:
1. **Clock Mode (Default):** Displays an analog clock (outline and hour, minute, second hands) and a digital time readout. Clock synchronization occurs over Wi-Fi via Adafruit IO NTP.
2. **Countdown Mode:** When either MatrixPortal button (`BUTTON_UP` or `BUTTON_DOWN`) is pressed, starts a countdown timer (default 5 minutes). Renders a progress bar and remaining time in seconds/minutes.
3. **Train Mode:** When countdown reaches zero, plays an animated train sprite (`train.bmp`) across the LED matrix for a configurable number of loops before reverting to clock display.
4. **Nightly Maintenance:** Periodically (at 3:00 AM) resynchronizes system time over NTP and triggers garbage collection (`gc.collect()`).

### Hardware Target
- **Board:** Adafruit MatrixPortal S3 (ESP32-S3)
- **Display:** 64x32 RGB LED Matrix (HUB-75, 6mm pitch)
- **Runtime:** CircuitPython 10.0.0 (`adafruit-circuitpython-matrixportal_m4-en_US-10.0.0` or S3 variant)

---

## 2. Directory & Key File Structure

```
├── main.py                     # Entry point for CircuitPython execution
├── application.py              # Application lifecycle, main loop, state machine
├── display.py                  # Display driver: ClockHand, analog/digital clock, countdown, train sprite
├── buttons.py                  # Hardware button state helpers
├── logging_extra.py            # Logger setup (stdout / StreamHandler & Adafruit IO feed push)
├── time_conversion.py          # Relative time formatting utilities
├── time_conversion_test.py     # CPython unit tests for time conversion
├── train_predictor.py          # Direction enum & direction string utility
├── settings.toml               # Wi-Fi credentials & Adafruit IO secrets (git-ignored)
├── install.sh                  # Deployment script to sync project files to mounted CIRCUITPY drive
├── install_circuitpython_lib.sh# Fetches and syncs Adafruit CircuitPython bundle libraries to CIRCUITPY
├── log_tty.sh                  # Shell script to stream and rotate logs from /dev/ttyACM0
├── fonts/                      # BDF bitmap fonts (e.g. 4x6.bdf, 6x10.bdf)
├── background.bmp              # Background graphic asset
├── train.bmp                   # Sprite sheet for train animation
└── testdata/                   # Test fixtures/data
```

---

## 3. Critical Conventions & Constraints

### CircuitPython vs. Standard CPython
- **Entrypoint name:** The codebase deliberately uses `main.py` rather than `code.py`. Naming it `code.py` causes name collision with standard library `code.py` in CPython (which breaks VS Code's test adapter with `ModuleNotFoundError: No module named 'microcontroller'`). **Do not rename `main.py` back to `code.py`**.
- **Dependency Injection for Hardware Libs:** CircuitPython modules (`board`, `displayio`, `adafruit_matrixportal`, `digitalio`, `microcontroller`) are generally not importable in standard desktop CPython. To maintain desktop testability, pass hardware/library dependencies into constructors (`ApplicationDependencies`, `DisplayDependencies`, `LoggerDependencies`) rather than instantiating hardware objects inside business logic classes.
- **Resource Constraints & Garbage Collection:** Memory on microcontrollers is constrained. Explicit `gc.collect()` calls are placed after display initialization and in nightly maintenance routines. Avoid heavy allocations inside the tight `_run_loop` or animation frames.
- **Display Refresh Constraints:** Noticeable screen flickering or jitter occurs if text fields or graphic objects are updated without their underlying values changing. Always guard display updates with dirty checks (e.g., compare formatted string before calling `_matrix_portal.set_text()`, compare angle before updating `ClockHand.angle`). A short `time.sleep(0.1)` is required in the main loop to yield cycles for display refreshing.
- **File System Writes & Flash Wear:** Avoid logging to the local FAT filesystem (`/`). Local disk writes cause LED flickering due to power/bus contention and wear out the microcontroller's SPI flash. Logs should go to stdout (`StreamHandler`) and Adafruit IO (`AIOHandler`).
- **Button Polling:** Hardware interrupts and complex async loops are avoided to keep runtime overhead low. Buttons are pulled up (`Pull.UP`, active low) and polled synchronously in the loop.

---

## 4. Development & Testing Commands

### Running Unit Tests
Unit tests run using standard CPython (tested with Python 3.13+):
```bash
python3 -m unittest discover -p "*_test.py"
```

### Flashing & Deploying to Hardware
1. **Prepare Secrets:** Ensure `settings.toml` exists in the repository root with valid Wi-Fi and Adafruit IO configuration:
   ```toml
   CIRCUITPY_WIFI_SSID = "your_ssid"
   CIRCUITPY_WIFI_PASSWORD = "your_password"
   ADAFRUIT_AIO_USERNAME = "your_aio_username"
   ADAFRUIT_AIO_KEY = "your_aio_key"
   ```
2. **Install CircuitPython Libraries (First-time or Update):**
   Mount the device (default path: `/run/media/anitschk/CIRCUITPY`) and run:
   ```bash
   ./install_circuitpython_lib.sh
   ```
3. **Deploy Code & Assets:**
   Synchronize local scripts, fonts, and assets to the device using:
   ```bash
   ./install.sh
   ```
   *(Note: `install.sh` uses `rsync --inplace` to prevent IO errors on CircuitPython's USB mass storage emulation).*

### Debugging & Serial Monitoring
- **Interactive REPL & Serial Console:**
  ```bash
  screen /dev/ttyACM0
  ```
  *(Check `/dev/ttyACM*` if reconnected under an alternate device index).*
- **Continuous Logging to File:**
  ```bash
  ./log_tty.sh
  ```

---

## 5. Development Guidelines & Change Protocol

When modifying or extending this codebase, adhere to the following rules:

1. **Keep Unit Tests Updated & Passing:**
   - Always run existing unit tests with `python3 -m unittest discover -p "*_test.py"` to ensure no regressions.
   - Any new or modified business logic, time math, or utility functionality must be accompanied by corresponding unit tests (named `*_test.py`).
   - Maintain the dependency injection pattern so new logic can be tested in standard CPython without importing hardware packages (`board`, `displayio`, etc.).

2. **Synchronize Documentation (`AGENTS.md` & `README.md`):**
   - **`AGENTS.md`**: Whenever architecture, coding conventions, deployment procedures, script usages, or critical constraints change, update this document to keep agent and developer context accurate.
   - **`README.md`**: Whenever user-facing features, hardware configurations, wiring, secrets, setup instructions, or dependencies change, update `README.md` accordingly.
   - If files are added or removed from the repository, ensure both `AGENTS.md` (directory structure) and `install.sh` (rsync file list) are updated.

