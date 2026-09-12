"""Boot configuration for the fable-r2d2 KB2040.

Runs once, before ``code.py``, and enables the second USB CDC endpoint.  The Pi
talks to that endpoint (``/dev/ttyACM1`` on Raspberry Pi OS) so the REPL console
on the first endpoint stays free for debugging.

Copy this file to the root of CIRCUITPY next to ``code.py``.  A change here only
takes effect after a hard reset or a power cycle, not after a soft reload.
"""

import usb_cdc

usb_cdc.enable(console=True, data=True)
