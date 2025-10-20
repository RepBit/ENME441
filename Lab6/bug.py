import RPi.GPIO as GPIO
import time
from shifter import Bug

# --------------------------
# GPIO input pins
# --------------------------
s1_pin = 17   # Switch to start/stop the bug
s2_pin = 27   # Switch to toggle wrap mode
s3_pin = 22   # Switch to increase speed (reduce delay)

GPIO.setmode(GPIO.BCM)
GPIO.setup(s1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --------------------------
# Instantiate Bug
# --------------------------
bug = Bug(serialPin=23, clockPin=24, latchPin=25, timestep=0.1)

prev_s2_state = GPIO.input(s2_pin)

try:
    while True:
        # --- Read switch states ---
        s1 = GPIO.input(s1_pin)
        s2 = GPIO.input(s2_pin)
        s3 = GPIO.input(s3_pin)

        # --- Start/stop Bug ---
        if s1:
            bug.running = True
        else:
            bug.running = False
            bug.clear()

        # --- Toggle wrap mode on rising edge of s2 ---
        if s2 != prev_s2_state and s2 == 1:
            bug.isWrapOn = not bug.isWrapOn
        prev_s2_state = s2

        # --- Adjust speed ---
        bug.timestep = 0.033 if s3 else 0.1  # 3x faster when s3 pressed

        # --- Step Bug if running ---
        bug.step()

        time.sleep(bug.timestep)

except KeyboardInterrupt:
    bug.stop()
