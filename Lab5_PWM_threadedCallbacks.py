GPIO.setmode(GPIO.BCM)

pin = 25
freq = 0.2
PWM_freq = 500

GPIO.setup(pin, GPIO.OUT)
pwm = GPIO.PWM(pin, PWM_freq)
pwm.start(0)

try:
    while True:
        t = time.time()
        B = math.sin(2 * math.pi * freq * t) ** 2
        duty = B * 100
        pwm.ChangeDutyCycle(duty)

except KeyboardInterrupt:
    print("\nExiting")
  
pwm.stop()
GPIO.cleanup()



