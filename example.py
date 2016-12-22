from neopixel import *
import time

LED_COUNT = 100
# All args after the first are ignored, but allowed for compatibility.
strip = Adafruit_NeoPixel(LED_COUNT)
# Start the simulation.
strip.begin()
i = pi = 0
while True:
    strip.setPixelColorRGB(pi, 0, 0, 0)
    strip.setPixelColorRGB(i, 255, 255, 255)
    strip.show()

    pi, i = i, (i + 1) % LED_COUNT
    time.sleep(0.1)
