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
    """Encapsulates the behavior of a moving LED ("bug") on an 8-bit LED bar."""

    def __init__(self, serialPin, clockPin, latchPin, timestep=0.1, x=3, isWrapOn=False):
        """
        Initialize a Bug that moves an LED on a shift register display.

        Args:
            serialPin (int): GPIO pin for serial input to shift register.
            clockPin (int): GPIO pin for clock.
            latchPin (int): GPIO pin for latch.
            timestep (float): Time delay between steps (default=0.1s).
            x (int): Starting LED position (0–7, default=3).
            isWrapOn (bool): If True, wraps around edges; if False, stops at edges.
        """
        self.timestep = timestep
        self.x = x
        self.isWrapOn = isWrapOn
        self.__shifter = Shifter(serialPin, clockPin, latchPin)
        self.__running = False

        # LED bit patterns for 8-bit output
        self.__led_array = [1, 2, 4, 8, 16, 32, 64, 128]

    # --------------------------
    # Private helper methods
    # --------------------------
    def __display(self):
        """Light up LED at current position."""
        self.__shifter.shiftByte(self.__led_array[self.x])

    def __clear(self):
        """Turn off all LEDs."""
        self.__shifter.shiftByte(0)

    def __move(self):
        """Perform one random step (-1 or +1) and update position."""
        step = random.choice([-1, 1])
        new_x = self.x + step

        if self.isWrapOn:
            new_x %= 8  # wrap around
        else:
            new_x = max(0, min(7, new_x))  # clamp between 0–7

        self.x = new_x

    # --------------------------
    # Public methods
    # --------------------------
    def start(self):
        """Start the bug's random walk motion."""
        self.__running = True
        print("Bug started! Press Ctrl+C to stop.")
        try:
            while self.__running:
                self.__display()
                time.sleep(self.timestep)
                self.__move()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop bug motion and clear display."""
        self.__running = False
        self.__clear()
        GPIO.cleanup()
        print("\nBug stopped and GPIO cleaned up.")


'''
if __name__ == "__main__":
  try:
    shifter = Shifter(serialPin=23, clockPin=25, latchPin=24)
    pattern = 0b01100110

    shifter.shiftByte(pattern)
    
    while 1: pass
      
  except KeyboardInterrupt:
        GPIO.cleanup()
'''


