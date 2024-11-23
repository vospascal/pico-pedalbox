# SPDX-FileCopyrightText: 2018 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`Gamepad`
====================================================

* Author(s): Dan Halbert
"""

import struct
import time

from adafruit_hid import find_device

class Gamepad:
    # ... existing code ...

    def __init__(self, devices):
        """Create a Gamepad object that will send USB gamepad HID reports.

        Devices can be a list of devices that includes a gamepad device or a gamepad device
        itself. A device is any object that implements ``send_report()``, ``usage_page`` and
        ``usage``.
        """
        self._gamepad_device = find_device(devices, usage_page=0x1, usage=0x05)

        # Reuse this bytearray to send gamepad reports.
        # Typically controllers start numbering buttons at 1 rather than 0.
        # report[0] buttons 1-8 (LSB is button 1)
        # report[1] buttons 9-11
        self._report = bytearray(2)

        # Remember the last report as well, so we can avoid sending
        # duplicate reports.
        self._last_report = bytearray(2)

        # Store settings separately before putting into report. Saves code
        # especially for buttons.
        self._buttons_state = 0

        # Send an initial report to test if HID device is ready.
        # If not, wait a bit and try once more.
        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    def press_buttons(self, *buttons):
        """Press and hold the given buttons."""
        for button in buttons:
            self._buttons_state |= 1 << (self._validate_button_number(button) - 1)
        self._send()

    def release_buttons(self, *buttons):
        """Release the given buttons."""
        for button in buttons:
            self._buttons_state &= ~(1 << (self._validate_button_number(button) - 1))
        self._send()

    def release_all_buttons(self):
        """Release all the buttons."""
        self._buttons_state = 0
        self._send()

    def click_buttons(self, *buttons):
        """Press and release the given buttons."""
        self.press_buttons(*buttons)
        self.release_buttons(*buttons)

    def reset_all(self):
        """Release all buttons."""
        self._buttons_state = 0
        self._send(always=True)

    def _send(self, always=False):
        struct.pack_into(
            "<H",  # Format: unsigned short (2 bytes)
            self._report,  # The bytearray to pack into
            0,  # Offset
            self._buttons_state & 0x0FFF,  # Mask to ensure only 12 bits are used
        )

        # Debug print to verify the report content
        print(f"Report: {self._report.hex()}")
        
        if always or self._last_report != self._report:
            self._gamepad_device.send_report(self._report)
            self._last_report[:] = self._report

    @staticmethod
    def _validate_button_number(button):
        if not 1 <= button <= 12:  # Updated to allow 12 buttons
            raise ValueError("Button number must be in range 1 to 12")
        return button
