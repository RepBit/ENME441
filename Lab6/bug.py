import RPi.GPIO as GPIO
import time
from shifter import Bug  # Assuming your previous code is in shifter.py

# --- GPIO setup for switches ---
s1_pin = 5  # On/off switch
s2_pin = 6  # Wrap toggle
s3_pin = 13 # Speed multiplier

GPIO.setmode(GPIO.BCM)
for pin in [s1_pin, s2_pin, s3_pin]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # use pull-down resistors

# --- Initialize Bug ---
bug = Bug(serialPin=17, clockPin=27, latchPin=22)  # adjust pins for your shift register

# Track previous state of s2 to detect changes
prev_s2_state = GPIO.input(s2_pin)

try:
    while True:
        s1_state = GPIO.input(s1_pin)
        s2_state = GPIO.input(s2_pin)
        s3_state = GPIO.input(s3_pin)

        # --- Handle Bug on/off ---
        if s1_state and not bug._Bug__running:  # start if not running
            print("Starting Bug")
            bug._Bug__running = True
            bug._Bug__shifter.shiftByte(0)
        elif not s1_state and bug._Bug__running:  # stop if running
            print("Stopping Bug")
            bug._Bug__running = False
            bug._Bug__shifter.shiftByte(0)

        # --- Handle wrapping toggle on s2 edge ---
        if s2_state != prev_s2_state and s2_state == 1:  # rising edge
            bug.isWrapOn = not bug.isWrapOn
            print(f"Wrap toggled: {bug.isWrapOn}")
        prev_s2_state = s2_state

        # --- Handle speed multiplier ---
        if s3_state:
            timestep = max(bug.timestep / 3, 0.01)
        else:
            timestep = bug.timestep

        # --- Move Bug if running ---
        if bug._Bug__running:
            import random
            step = random.choice([-1, 1])
            new_x = bug.x + step

            if bug.isWrapOn:
                if new_x < 0: new_x = 7
                elif new_x > 7: new_x = 0
            else:
                new_x = max(0, min(7, new_x))

            bug.x = new_x
            bug._Bug__shifter.shiftByte(bug._Bug__led_array[bug.x])

        time.sleep(timestep)

except KeyboardInterrupt:
    bug.stop()
    print("Program terminated by user")
