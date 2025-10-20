import RPi.GPIO as GPIO
import time
from Bug import Bug  # assuming your Bug class is saved as bug_class.py

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
s1, s2, s3 = 5, 6, 13  # example input pins, change as needed

GPIO.setup(s1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --- Instantiate Bug ---
bug = Bug(serialPin=23, clockPin=25, latchPin=24)  # uses default timestep=0.1, x=3, isWrapOn=False

# --- State Tracking ---
prev_s2_state = GPIO.input(s2)
bug_running = False

print("Bug control started:")
print(" s1: On/Off | s2: Toggle wrap | s3: Speed x3\nPress Ctrl+C to exit.")

try:
    while True:
        # --- Read switch states ---
        s1_state = GPIO.input(s1)
        s2_state = GPIO.input(s2)
        s3_state = GPIO.input(s3)

        # (a) s1 → Turn Bug on/off
        if s1_state and not bug_running:
            bug_running = True
            print("Bug ON")
        elif not s1_state and bug_running:
            bug_running = False
            bug.stop()
            print("Bug OFF")

        # (b) s2 → Flip wrapping when state changes
        if s2_state != prev_s2_state:
            if s2_state:  # on rising edge
                bug.isWrapOn = not bug.isWrapOn
                print(f"Wrap mode {'ON' if bug.isWrapOn else 'OFF'}")
            prev_s2_state = s2_state

        # (c) s3 → Adjust speed (3x faster when pressed)
        if s3_state:
            bug.timestep = 0.1 / 3
        else:
            bug.timestep = 0.1

        # --- Move the bug if active ---
        if bug_running:
            bug._Bug__display()  # use Bug’s private display method to show position
            time.sleep(bug.timestep)
            bug._Bug__move()     # random step
        else:
            time.sleep(0.05)

except KeyboardInterrupt:
    bug.stop()
    GPIO.cleanup()
    print("\nProgram stopped and GPIO cleaned up.")
