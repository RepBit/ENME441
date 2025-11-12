# stepper_class_shiftregister_multiprocessing.py
#
# Updated to:
# - Use multiprocessing.Value for shared shifter outputs and per-motor angle & step_state
# - Allow interleaved simultaneous stepping across motors by making each step
#   a short critical section
# - Implement goAngle(a) to travel via the shortest path
#
# Note: You must create the shared Stepper.shifter_outputs Value in main (see example below)
# and pass the Shifter object and a multiprocessing.Lock() to each Stepper.

import time
import multiprocessing
from shifter import Shifter   # your Shifter class that has shiftByte()

class Stepper:
    """
    See course notes. Key changes:
    - shifter_outputs is a multiprocessing.Value('I', 0) (shared across processes)
    - each instance uses multiprocessing.Value for angle and step_state
    - __step() uses the provided lock to protect the shared shifter_outputs and the
      actual call to shiftByte(); the lock is held only while updating outputs and
      calling shiftByte, so multiple motors can take turns stepping.
    """

    # Class attributes (set shifter_outputs externally in main)
    num_steppers = 0        # track number of Steppers instantiated
    shifter_outputs = None  # will be multiprocessing.Value('I',0) initialized in main
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001] # CCW sequence
    # delay in seconds between individual steps
    delay = 1200/1e6          # 1200 microseconds -> 0.0012 seconds
    steps_per_degree = 4096.0/360.0    # 4096 steps/rev * 1/360 rev/deg

    def __init__(self, shifter, lock):
        self.s = shifter           # Shifter instance
        # Use multiprocessing.Value so child processes modify the real value
        self.angle = multiprocessing.Value('d', 0.0)       # current output shaft angle (degrees)
        self.step_state = multiprocessing.Value('i', 0)   # index into seq [0..7]
        self.shifter_bit_start = 4 * Stepper.num_steppers  # starting bit position (nibble)
        self.lock = lock           # multiprocessing Lock to protect shift register update

        Stepper.num_steppers += 1   # increment the instance count

    # Signum function:
    def __sgn(self, x):
        if x == 0: return 0
        return int(abs(x)/x)

    # Move a single +/-1 step in the motor sequence (small critical section only)
    def __step(self, dir):
        # Compute new step_state and update shared shifter outputs under lock
        with self.lock:
            # update step_state (shared)
            new_state = (self.step_state.value + dir) % 8
            self.step_state.value = new_state

            # Clear this motor's 4 bits in the shared shifter_outputs
            mask = 0b1111 << self.shifter_bit_start
            Stepper.shifter_outputs.value &= ~mask

            # OR in the new nibble for this motor
            pattern = Stepper.seq[self.step_state.value] << self.shifter_bit_start
            Stepper.shifter_outputs.value |= pattern

            # Send the byte to the shift register
            # Note: Shifter.shiftByte should accept an integer 0..255
            self.s.shiftByte(Stepper.shifter_outputs.value)

            # Update shared angle (in degrees)
            # Use steps_per_degree to convert one step -> degrees
            delta_angle = dir / Stepper.steps_per_degree
            self.angle.value = (self.angle.value + delta_angle) % 360

    # Rotates by delta degrees (non-blocking; spawns a new process)
    # NOTE: __rotate does the real work; rotate() starts the process
    def __rotate(self, delta):
        # delta: signed degrees (+CW or + depending on sign convention)
        numSteps = int(round(abs(delta) * Stepper.steps_per_degree))
        dir = self.__sgn(delta)
        for _ in range(numSteps):
            self.__step(dir)
            time.sleep(Stepper.delay)  # delay in seconds

    def rotate(self, delta):
        # spawn a separate process for rotation so motors can run concurrently
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()
        return p

    # Move to an absolute angle taking the shortest possible path:
    def goAngle(self, angle_target):
        """
        Command the motor to go to absolute angle_target (degrees, can be negative or outside 0..359).
        We compute the shortest signed delta in degrees in range [-180, +180] and call rotate(delta).
        Because angle is a multiprocessing.Value, we read the current angle using self.angle.value.
        """
        # normalize target to 0..360
        t = angle_target % 360.0
        current = self.angle.value % 360.0

        # compute shortest delta: result in (-180, 180]
        delta = (t - current + 180.0) % 360.0 - 180.0
        # If exactly -180, choose +180 (arbitrary)
        if delta == -180.0:
            delta = 180.0

        return self.rotate(delta)

    # Set the motor zero point (shared Value update)
    def zero(self):
        self.angle.value = 0.0
        # Optionally, reset step_state to 0
        self.step_state.value = 0


# -------------------------
# Example use (main guard)
# -------------------------
if __name__ == '__main__':
    # Example wiring & runtime setup:
    # - Create Shifter object (adjust pins for your Pi)
    # - Create a multiprocessing.Value for shared shifter outputs
    # - Create a Lock (shared) and two Stepper instances
    #
    # Make sure to run this on the Pi where the hardware is connected.

    s = Shifter(data=16, clock=20, latch=21)   # match your wiring

    # Create shared objects before creating Stepper instances:
    Stepper.shifter_outputs = multiprocessing.Value('I', 0)  # unsigned int, shared among processes
    lock = multiprocessing.Lock()

    # Instantiate steppers
    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    # Zero them
    m1.zero()
    m2.zero()

    # Start motors using goAngle; returned Process objects can be joined if desired
    # These calls should cause both motors to operate simultaneously (interleaved steps)
    p1 = m1.goAngle(90)
    p2 = m1.goAngle(-45)
    p3 = m2.goAngle(-90)
    p4 = m2.goAngle(45)
    p5 = m1.goAngle(-135)
    p6 = m1.goAngle(135)
    p7 = m1.goAngle(0)

    # Wait for all processes to finish (optional)
    for p in (p1, p2, p3, p4, p5, p6, p7):
        if p is not None:
            p.join()

    print("All rotations complete.")
