import time
import random
import RPi.GPIO as GPIO
from shifter import Shifter

# --- Setup ---
# Instantiate your Shifter (serial, clock, latch pins)
shifter = Shifter(serialPin=23, clockPin=25, latchPin=24)

# --- Random Walk Parameters ---
position = 0              # start at LED position 0 (rightmost)
num_leds = 8              # total number of LEDs
delay = 0.05              # seconds per time step
array = [1, 2, 4, 8, 16, 32, 64, 128]

shifter.shiftByte(1);

try:
    while True:
        step = random.choice([-1, 1])

        position += step

        if position < 1:
            position = 1
        elif position > num_leds-1:
            position = num_leds-1
        
        shifter.shiftByte(array[position-1])
        
        time.sleep(delay)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nProgram stopped and GPIO cleaned up.")


'''
try:
    while True:
        # Compute pattern: single '1' bit representing the active LED
        pattern = 1 << position
        shifter.shiftByte(pattern)

        # Randomly decide to move left (-1) or right (+1)
        step = random.choice([-1, 1])
        position += step

        # Prevent moving beyond the edges (0 to 7)
        if position < 0:
            position = 0
        elif position > num_leds - 1:
            position = num_leds - 1

        time.sleep(delay)
    '''
