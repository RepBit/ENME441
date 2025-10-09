import RPi.GPIO as GPIO
import math
import time

GPIO.setmode(GPIO.BCM)

pin1 = 25
pin2 = 24
freq = 0.2
PWM_freq = 500
phi = math.pi/11

GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)

pwm1 = GPIO.PWM(pin1, PWM_freq)
pwm2 = GPIO.PWM(pin2, PWM_freq)

try:
    pwm1.start(0)
    pwm2.start(0)

    while True:
        t = time.time()
        B1 = math.sin(2 * math.pi * freq * t) ** 2
        B2 = math.sin(2 * math.pi * freq * t - phi) ** 2
        
        duty1 = B1 * 100
        duty2 = B2 * 100
        
        pwm1.ChangeDutyCycle(duty1)
        pwm2.ChangeDutyCycle(duty2)


except KeyboardInterrupt:
    print("\nExiting")
  
pwm1.stop()
pwm2.stop()
GPIO.cleanup()






