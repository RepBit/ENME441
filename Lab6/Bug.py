import time
import random
import RPi.GPIO as GPIO
from shifter import Shifter

class Bug:
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
        self.__shifter = Shifter(serialPin, clockPin, latchPin)  # private composition
        self.__running = False

        # 8-bit LED pattern (bit shifted positions)
        self.__led_array = [1, 2, 4, 8, 16, 32, 64, 128]

    def __display(self):
        """Private helper to display the LED at current position."""
        self.__shifter.shiftByte(self.__led_array[self.x])

    def __clear(self):
        """Private helper to turn off all LEDs."""
        self.__shifter.shiftByte(0)

    def __move(self):
        """Private helper for one random step (-1 or +1) with boundary logic."""
        step = random.choice([-1, 1])
        new_x = self.x + step

        if self.isWrapOn:
            # Wrap around from one edge to the other
            new_x %= 8
        else:
            # Clamp movement within the LED range
            if new_x < 0:
                new_x = 0
            elif new_x > 7:
                new_x = 7

        self.x = new_x

    def start(self):
        """Start the bug’s random walk movement."""
        self.__running = True
        print("Bug started! Press Ctrl+C to stop.")
        try:
            while self.__running:
                self.__display()
                self.__move()
                time.sleep(self.timestep)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop bug movement and clear LEDs."""
        self.__running = False
        self.__clear()
        GPIO.cleanup()
        print("\nBug stopped and GPIO cleaned up.")
