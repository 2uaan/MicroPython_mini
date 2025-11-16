from machine import Pin, PWM
import time

class MG90S:
    """
    MicroPython class to control an MG90S servo motor.
    Works with Raspberry Pi Pico or any MicroPython board.
    """
    def __init__(self, pin_num: int, min_us: int = 500, max_us: int = 2500, freq: int = 50):
        """
        :param pin_num: GPIO pin number connected to servo signal wire
        :param min_us: Minimum pulse width in microseconds (servo 0°)
        :param max_us: Maximum pulse width in microseconds (servo 180°)
        :param freq: PWM frequency in Hz (50 Hz for most servos)
        """
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(freq)
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq
        self.period_us = 1_000_000 // freq  # Period in microseconds

    def deinit(self):
        """Stop PWM output."""
        self.pwm.deinit()

    def angle(self, degrees: float):
        """
        Move servo to a specific angle (0° to 180°).
        Values outside range are clamped.
        """
        if degrees < 0:
            degrees = 0
        elif degrees > 180:
            degrees = 180

        # Map angle to pulse width
        us = self.min_us + (self.max_us - self.min_us) * (degrees / 180.0)
        duty_u16 = int(us * 65535 // self.period_us)
        self.pwm.duty_u16(duty_u16)



    

