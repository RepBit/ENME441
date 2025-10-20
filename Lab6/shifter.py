import time
import random
import RPi.GPIO as GPIO
from shifter import Shifter

class Bug:
    def __init__(self, serialPin, clockPin, latchPin, timestep=0.1, x=3, isWrapOn=False):
        """ Initialize a Bug that moves an LED on a shift register display. """
        self.timestep = timestep
        self.x = x
        self.isWrapOn = isWrapOn
        self._shifter = Shifter(serialPin, clockPin, latchPin)  # composition
        self.running = False  # public flag

        # 8-bit LED pattern
        self.led_array = [1, 2, 4, 8, 16, 32, 64, 128]

    # --- Private helpers ---
    def __display(self):
        self._shifter.shiftByte(self.led_array[self.x])

    def __clear(self):
        self._shifter.shiftByte(0)

    def __move(self):
        step = random.choice([-1, 1])
        new_x = self.x + step
        if self.isWrapOn:
            new_x %= 8
        else:
            new_x = max(0, min(7, new_x))
        self.x = new_x

    # --- Public control methods ---
    def start_step(self):
        """Do a single movement step (display + move)."""
        if not self.running:
            return
        self.__display()
        self.__move()

    def start(self):
        """Run the Bug continuously (blocking)."""
        self.running = True
        print("Bug started! Press Ctrl+C to stop.")
        try:
            while self.running:
                self.start_step()
                time.sleep(self.timestep)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop Bug movement and clear LEDs."""
        self.running = False
        self.__clear()
        GPIO.cleanup()
        print("\nBug stopped and GPIO cleaned up.")
