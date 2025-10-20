import RPi.GPIO as GPIO
import time
from shifter import Bug

# --------------------------
# GPIO input pins
# --------------------------
s1_pin = 17   # Switch to start/stop the bug
s2_pin = 27   # Switch to toggle wrap mode
s3_pin = 22  # Switch to increase speed (reduce delay)

GPIO.setmode(GPIO.BCM)
GPIO.setup(s1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --------------------------
# Instantiate Bug
# --------------------------
bug = Bug(serialPin=23, clockPin=24, latchPin=25, timestep=0.1)

# Track previous state of s2 to detect changes
prev_s2_state = GPIO.input(s2_pin)

try:
    while True:
        # --- Read switch states ---
        s1 = GPIO.input(s1_pin)
        s2 = GPIO.input(s2_pin)
        s3 = GPIO.input(s3_pin)

        # --- Control bug start/stop ---
        if s1 and not bug._Bug__running:  # private attribute access
            bug._Bug__running = True
        elif not s1 and bug._Bug__running:
            bug._Bug__running = False
            bug._Bug__clear()

        # --- Toggle wrap mode when s2 changes ---
        if s2 != prev_s2_state:
            bug.isWrapOn = not bug.isWrapOn
            prev_s2_state = s2

        # --- Adjust speed when s3 is on ---
        if s3:
            bug.timestep = 0.1/3
        else:
            bug.timestep = 0.1  # default speed

        # --- If bug is running, move & display ---
        if bug._Bug__running:
            bug._Bug__display()
            bug._Bug__move()

        time.sleep(bug.timestep)

except KeyboardInterrupt:
    bug.stop()
