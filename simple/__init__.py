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
    def __init__(self, devices):
        """Create a Gamepad object that will send USB gamepad HID reports.

        Devices can be a list of devices that includes a gamepad device or a gamepad device
        itself. A device is any object that implements ``send_report()``, ``usage_page`` and
        ``usage``.
        """
        self._gamepad_device = find_device(devices, usage_page=0x1, usage=0x05)

        # Reuse this bytearray to send gamepad reports.
        # Report structure:
        #   Byte 0: RX
        #   Byte 1: RY
        #   Byte 2: RZ
        self._report = bytearray(3)

        # Remember the last report as well, so we can avoid sending
        # duplicate reports.
        self._last_report = bytearray(3)

        # Store axis states separately for easier manipulation.
        self._rx = 0
        self._ry = 0
        self._rz = 0

        # Send an initial report to test if HID device is ready.
        # If not, wait a bit and try once more.
        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    def set_axes(self, rx, ry, rz):
        """Set the RX, RY, and RZ axis values (0-255)."""
        self._rx = self._validate_axis_value(rx)
        self._ry = self._validate_axis_value(ry)
        self._rz = self._validate_axis_value(rz)
        self._send()

    def reset_all(self):
        """Reset all axes to 0."""
        self._rx = 0
        self._ry = 0
        self._rz = 0
        self._send(always=True)

    def _send(self, always=False):
        # Pack RX, RY, RZ axes
        self._report[0] = self._rx
        self._report[1] = self._ry
        self._report[2] = self._rz

        # Debug print to verify the report content
        print(f"Report: {self._report.hex()}")

        # Only send the report if it's different from the last one, unless `always` is True
        if always or self._last_report != self._report:
            self._gamepad_device.send_report(self._report)
            self._last_report[:] = self._report

    @staticmethod
    def _validate_axis_value(value):
        if not 0 <= value <= 255:
            raise ValueError("Axis value must be in range 0 to 255")
        return value
