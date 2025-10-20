import RPi.GPIO as GPIO
import time

class Shifter:
  def __init__(self, serialPin, clockPin, latchPin):
    self.serialPin = serialPin
    self.clockPin = clockPin
    self.latchPin = latchPin

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.serialPin, GPIO.OUT)
    GPIO.setup(self.clockPin, GPIO.OUT, initial=0)
    GPIO.setup(self.latchPin, GPIO.OUT, initial=0)
  
  def __ping(self, pin): #_private
    GPIO.output(pin, 1)
    time.sleep(0)
    GPIO.output(pin, 0)

  def shiftByte(self, b): #public
    for i in range(8):
      GPIO.output(self.serialPin, b & (1 << i))
      self.__ping(self.clockPin)    # add bit to register
    self.__ping(self.latchPin)      # send register to output


if __name__ == "__main__":
  try:
    shifter = Shifter(serialPin=23, clockPin=25, latchPin=24)
    pattern = 0b01100110

    shifter.shiftByte(pattern)
    
    while True:
            pass
  
  except KeyboardInterrupt:
        GPIO.cleanup()



