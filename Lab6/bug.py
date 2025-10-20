import RPi.GPIO as GPIO
import time
from shifter import Bug  # assuming your previous code is in shifter.py

# --- GPIO setup ---
s1_pin = 5  # Switch to turn Bug on/off
s2_pin = 6  # Switch to toggle wrapping
s3_pin = 13 # Switch to increase speed

GPIO.setmode(GPIO.BCM)
for pin in [s1_pin, s2_pin, s3_pin]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --- Initialize Bug ---
bug = Bug(serialPin=17, clockPin=27, latchPin=22)  # example pins
bug_process_running = False
original_timestep = bug.timestep

# Track previous state for edge detection (for s2)
prev_s2_state = GPIO.input(s2_pin)

try:
    while True:
        s1 = GPIO.input(s1_pin)
        s2 = GPIO.input(s2_pin)
        s3 = GPIO.input(s3_pin)
        
        # --- Turn Bug on/off ---
        if s1 and not bug_process_running:
            # Start bug in a separate thread so we can continue monitoring switches
            import threading
            bug_thread = threading.Thread(target=bug.start)
            bug_thread.start()
            bug_process_running = True
        elif not s1 and bug_process_running:
            bug.stop()
            bug_process_running = False
            bug.timestep = original_timestep  # Reset speed
            
        # --- Toggle wrapping on s2 edge ---
        if s2 != prev_s2_state and s2 == 1:  # rising edge
            bug.isWrapOn = not bug.isWrapOn
            print(f"Wrapping toggled to: {bug.isWrapOn}")
        prev_s2_state = s2

        # --- Increase speed with s3 ---
        if s3:
            bug.timestep = original_timestep / 3
        else:
            bug.timestep = original_timestep

        time.sleep(0.05)  # short delay to debounce switches

except KeyboardInterrupt:
    bug.stop()
    GPIO.cleanup()
    print("Program terminated.")
