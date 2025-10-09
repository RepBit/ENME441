import RPi.GPIO as GPIO
import math
import time

GPIO.setmode(GPIO.BCM)

pinNum = [2, 3, 4, 14, 15, 18, 17, 27, 22, 23]
button = 24

freq = 0.2
PWM_freq = 500
phi = math.pi/11

for p in pinNum:    
    GPIO.setup(p, GPIO.OUT, initial = 0)

GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

pwms = [GPIO.PWM(p, PWM_freq) for p in pinNum]

def switch(pin):
    global phi
    phi *= -1
    print("Switch direction")

GPIO.add_event_detect(button, GPIO.RISING, callback=switch, bouncetime=100)

try:
    for pwm in pwms:
        pwn.start(0)
    
    while True:
        t = time.time()
        for i,p in enumerate(pwms):
            B = math.sin(2 * math.pi * freq * t - phi * i) ** 2
            p.ChangeDutyCycle(B*100)

except KeyboardInterrupt:
    print("\nExiting")
  
pwm.stop()
GPIO.cleanup()





