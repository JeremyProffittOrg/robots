"""Optional battery voltage sensing for the fable-r2d2 control server.

The Raspberry Pi has no analogue input, so pack voltage is read through an
ADS1115 16 bit I2C ADC (address 0x48) sitting across a resistor divider on the
12 V 7 Ah sealed lead acid pack.  The divider in the wiring set is 100 kilohm
over 15 kilohm, which turns a 15 V pack into 1.96 V at the ADC input, inside the
4.096 V full scale range.

The sensor is optional in the same way the head displays are: if the library or
the chip is absent the reason is logged once and ``read()`` returns ``None``, so
the web page shows "battery --" instead of a wrong number.
"""

import logging

LOGGER = logging.getLogger("r2d2.battery")

ADS1115_ADDRESS = 0x48
"""Default ADS1115 address with ADDR tied to ground."""

DIVIDER_TOP_OHMS = 100000.0
"""Upper resistor, pack positive to the ADC node."""

DIVIDER_BOTTOM_OHMS = 15000.0
"""Lower resistor, ADC node to ground."""

DIVIDER_RATIO = (DIVIDER_TOP_OHMS + DIVIDER_BOTTOM_OHMS) / DIVIDER_BOTTOM_OHMS
"""Multiply the measured node voltage by this to get pack voltage."""

# A 12 V sealed lead acid pack at rest: 12.7 V full, 11.8 V is about 20 percent
# left, 10.5 V is the discharge floor the datasheet allows.
FULL_VOLTS = 12.70
EMPTY_VOLTS = 11.60
CRITICAL_VOLTS = 11.20

SAMPLES = 4
"""Readings averaged per call, to settle the motor current ripple."""


class BatteryMonitor:
    """Reads pack voltage through an ADS1115, when one is fitted."""

    def __init__(self, address=ADS1115_ADDRESS, ratio=DIVIDER_RATIO):
        self.ratio = ratio
        self.channel = None
        self.reason = None
        self.last_volts = None

        try:
            import board
            import adafruit_ads1x15.ads1115 as ads1115
            from adafruit_ads1x15.analog_in import AnalogIn
        except (ImportError, NotImplementedError) as error:
            self.reason = (
                "battery sensing disabled: {0}; fix with 'pip install "
                "adafruit-circuitpython-ads1x15 Adafruit-Blinka'".format(error)
            )
            LOGGER.warning("%s", self.reason)
            return

        try:
            i2c = board.I2C()
            adc = ads1115.ADS1115(i2c, address=address)
            self.channel = AnalogIn(adc, ads1115.P0)
        except (OSError, RuntimeError, ValueError) as error:
            self.reason = "battery sensing disabled: no ADS1115 at 0x{0:02x} ({1})".format(
                address, error
            )
            LOGGER.warning("%s", self.reason)
            self.channel = None
            return
        LOGGER.info("battery monitor ready on ADS1115 0x%02x", address)

    def available(self):
        """True when a reading can be taken."""
        return self.channel is not None

    def read(self):
        """Return pack volts, or ``None`` when no sensor is fitted."""
        if self.channel is None:
            return None
        try:
            total = 0.0
            for _ in range(SAMPLES):
                total += self.channel.voltage
        except (OSError, RuntimeError) as error:
            LOGGER.error("battery read failed, disabling the sensor: %s", error)
            self.reason = "battery read failed: {0}".format(error)
            self.channel = None
            return None
        self.last_volts = (total / SAMPLES) * self.ratio
        return self.last_volts

    def state_of_charge(self, volts=None):
        """Rough remaining charge, 0.0 to 1.0, or ``None`` without a reading.

        Resting voltage is a coarse gauge on a lead acid pack and reads low
        under load, so this is only good enough to drive a bar on the web page.
        """
        if volts is None:
            volts = self.last_volts
        if volts is None:
            return None
        fraction = (volts - EMPTY_VOLTS) / (FULL_VOLTS - EMPTY_VOLTS)
        if fraction < 0.0:
            return 0.0
        if fraction > 1.0:
            return 1.0
        return fraction

    def snapshot(self):
        """Dictionary for the web page status line."""
        volts = self.read()
        return {
            "available": self.channel is not None,
            "volts": round(volts, 2) if volts is not None else None,
            "charge": self.state_of_charge(volts),
            "critical": volts is not None and volts < CRITICAL_VOLTS,
            "reason": self.reason,
        }
