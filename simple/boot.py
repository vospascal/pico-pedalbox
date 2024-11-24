# This is only one example of a gamepad descriptor.
# It may not suit your needs, or be supported on your host computer.
import usb_hid

GAMEPAD_REPORT_DESCRIPTOR = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop Controls)
    0x09, 0x05,        # Usage (Gamepad)
    0xA1, 0x01,        # Collection (Application)
    0x15, 0x00,        # Logical Minimum (0)
    0x26, 0xFF, 0x00,  # Logical Maximum (255)
    0x75, 0x08,        # Report Size (8 bits)
    0x95, 0x03,        # Report Count (3 fields: RX, RY, RZ)
    0x09, 0x33,        # Usage (RX - Rotation about X-axis)
    0x09, 0x34,        # Usage (RY - Rotation about Y-axis)
    0x09, 0x35,        # Usage (RZ - Rotation about Z-axis)
    0x81, 0x02,        # Input (Data, Variable, Absolute)
    0xC0               # End Collection
])

gamepad_descriptor = usb_hid.Device(
    report_descriptor=GAMEPAD_REPORT_DESCRIPTOR,
    usage_page=0x01,        # Generic Desktop Controls
    usage=0x05,             # Gamepad
    report_ids=(1,),        # Report ID is 1
    in_report_lengths=(3,), # 3 bytes: RX, RY, RZ
    out_report_lengths=(0,) # No output reports
)
