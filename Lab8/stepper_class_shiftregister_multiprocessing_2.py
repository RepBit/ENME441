# stepper_class_shiftregister_multiprocessing.py
#
# Enhanced version for simultaneous multi-stepper operation
# using shift registers and multiprocessing on Raspberry Pi.

import time
import multiprocessing
from shifter import Shifter  # your provided Shifter class


class Stepper:
    """
    Stepper motor class that supports simultaneous operation
    of multiple motors through a shared shift register.

    Each motor uses 4 bits of the shift register output.
    """

    # Class attributes:
    num_steppers = 0           # track number of Stepper instances
    shifter_outputs = 0        # global 8-bit output state
    seq = [0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001]  # CCW sequence
    delay = 1200 / 1e6         # delay between steps [s]
    steps_per_degree = 4096 / 360  # 4096 steps per revolution = 11.3778 steps/deg

    def __init__(self, shifter, lock):
        self.s = shifter
        self.lock = lock
        self.step_state = 0
        self.shifter_bit_start = 4 * Stepper.num_steppers
        self.angle = multiprocessing.Value('d', 0.0)  # shared float (double precision)
        Stepper.num_steppers += 1

    # Sign function:
    def __sgn(self, x):
        return 0 if x == 0 else int(abs(x) / x)

    # Perform one step (+1 or -1):
    def __step(self, direction):
        # update local sequence index
        self.step_state = (self.step_state + direction) % 8

        # clear this motor's bits:
        mask = ~(0b1111 << self.shifter_bit_start)
        Stepper.shifter_outputs &= mask

        # apply new 4-bit pattern to this motor:
        Stepper.shifter_outputs |= Stepper.seq[self.step_state] << self.shifter_bit_start

        # send data to the shift register:
        self.s.shiftByte(Stepper.shifter_outputs)

        # update shared angle
        with self.angle.get_lock():
            self.angle.value += direction / Stepper.steps_per_degree
            self.angle.value %= 360

    # Rotate by delta angle (relative move)
    def __rotate(self, delta):
        with self.lock:  # ensure atomic register access
            num_steps = int(Stepper.steps_per_degree * abs(delta))
            direction = self.__sgn(delta)

            for _ in range(num_steps):
                self.__step(direction)
                time.sleep(Stepper.delay)

    # Launch rotation as separate process
    def rotate(self, delta):
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()
        return p

    # Move to absolute angle (shortest path)
    def goAngle(self, target_angle):
        with self.angle.get_lock():
            current_angle = self.angle.value

        # Normalize target angle to [0, 360)
        target_angle %= 360

        # Find shortest rotation path
        delta = target_angle - current_angle
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        return self.rotate(delta)

    # Zero the motor’s internal angle tracking
    def zero(self):
        with self.angle.get_lock():
            self.angle.value = 0.0


# Example use:
if __name__ == '__main__':
    s = Shifter(data=16, latch=20, clock=21)
    lock = multiprocessing.Lock()

    # Instantiate 2 stepper motors:
    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    # Reset both to 0 degrees
    m1.zero()
    m2.zero()
    print("Motors initialized at angle 0°")

    # Example test: simultaneous moves
    p1 = m1.goAngle(90)
    p2 = m2.goAngle(180)

    # Wait for both to finish
    p1.join()
    p2.join()

    print(f"Final angles → m1: {m1.angle.value:.1f}°, m2: {m2.angle.value:.1f}°")

    # More sequence testing:
    m1.goAngle(135)
    m2.goAngle(45)
    m1.goAngle(0)
