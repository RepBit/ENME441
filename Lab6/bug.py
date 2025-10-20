import RPi.GPIO as GPIO
import time
from shifter import Bug

s1_pin = 17 
s2_pin = 27  
s3_pin = 22 

GPIO.setmode(GPIO.BCM)
GPIO.setup(s1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

bug = Bug(serialPin=23, clockPin=24, latchPin=25, timestep=0.1)

prev_s2_state = GPIO.input(s2_pin)

try:
    while True:
        s1 = GPIO.input(s1_pin)
        s2 = GPIO.input(s2_pin)
        s3 = GPIO.input(s3_pin)

        if s1 and not bug._Bug__running:
            bug._Bug__running = True
        elif not s1 and bug._Bug__running:
            bug._Bug__running = False
            bug._Bug__clear()

        if s2 != prev_s2_state:
            bug.isWrapOn = not bug.isWrapOn
            prev_s2_state = s2

        if s3:
            bug.timestep = 0.1/3
        else:
            bug.timestep = 0.1

        if bug._Bug__running:
            bug._Bug__display()
            bug._Bug__move()

        time.sleep(bug.timestep)

except KeyboardInterrupt:
    bug.stop()
