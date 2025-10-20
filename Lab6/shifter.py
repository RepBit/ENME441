import RPi.GPIO as GPIO
import time
import random

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

class Bug:
  def __init__(self, serialPin, clockPin, latchPin, timestep=0.1, x=3, isWrapOn=False):
    self.timestep = timestep
    self.x = x
    self.isWrapOn = isWrapOn
    self.__shifter = Shifter(serialPin, clockPin, latchPin)
    self.__running = False
    
    self.__led_array = [1, 2, 4, 8, 16, 32, 64, 128]
    
  def start(self):
    self.__running = True
    self.__shifter.shiftByte(0)
    try:
      while self.__running:
        step = random.choice([-1, 1])
        new_x = self.x + step
        
        if self.isWrapOn:
          if new_x < 0: new_x = 7
          elif new_x > 7: new_x = 0
          print("on")
        else:
          # Clamp movement within the LED range
          if new_x < 0: new_x = 0
          elif new_x > 7: new_x = 7
          print("off")
          
        self.x = new_x
        
        self.__shifter.shiftByte(self.__led_array[self.x])
      
        time.sleep(self.timestep)
        
    except KeyboardInterrupt:
          self.stop()

  def stop(self):
    self.__running = False
    self.__shifter.shiftByte(0)
    GPIO.cleanup()
    print("\nBug stopped and GPIO cleaned up.")










