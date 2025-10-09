'''import RPi.GPIO as GPIO
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
'''
import RPi.GPIO as GPIO
import math
import time

# Setup
GPIO.setmode(GPIO.BCM)
LED_PIN = 25         # Change if using a different GPIO pin
F_LED = 0.2          # Brightness wave frequency (Hz)
PWM_FREQ = 500       # PWM frequency for LED control (Hz)

# Configure pin and PWM
GPIO.setup(LED_PIN, GPIO.OUT)
pwm = GPIO.PWM(LED_PIN, PWM_FREQ)
pwm.start(0)         # start with LED off

print("Running... Press Ctrl+C to stop.")

try:
    while True:
        t = time.time()                   # current time (seconds)
        B = math.sin(2 * math.pi * F_LED * t) ** 2   # brightness 0–1
        duty = B * 100                    # convert to duty cycle (%)
        pwm.ChangeDutyCycle(duty)
        # no time.sleep(); updates continuously

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    pwm.stop()
    GPIO.cleanup()


