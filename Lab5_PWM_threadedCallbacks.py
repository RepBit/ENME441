import RPi.GPIO as GPIO
import math
import time

GPIO.setmode(GPIO.BCM)

p = 25
f = 0.2 # Hz
t = 1
B = math.pow(math.sin(2*math.pi*f*t),2)

GPIO.setup(p, GPIO.OUT)
pwm = GPIO.PWM(p, 500)

try:
  pwm.start(B)
  while True:
    pass
except KeyboardInterrupt:
    print("\nExiting")

pwm.stop()

GPIO.cleanup()



