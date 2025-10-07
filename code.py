import time
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)

# Create a new label with the color and text selected
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 2) - 1),
    scrolling=True,
)

SCROLL_DELAY = 0.03

while True:
    matrixportal.set_text('HELLO WORLD')
    matrixportal.set_text_color('#0846e4')
    matrixportal.scroll_text(SCROLL_DELAY)
