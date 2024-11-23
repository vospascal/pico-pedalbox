# This is only one example of a gamepad descriptor.
# It may not suit your needs, or be supported on your host computer.
import usb_hid

GAMEPAD_REPORT_DESCRIPTOR = bytes([
        0x05, 0x01,        # Usage Page (Generic Desktop)
        0x09, 0x05,        # Usage (Gamepad)
        0xA1, 0x01,        # Collection (Application)
        0x15, 0x00,        # Logical Minimum (0)
        0x26, 0xFF, 0x00,  # Logical Maximum (255)
        0x75, 0x08,        # Report Size (8)
        0x95, 0x03,        # Report Count (3)
        0x09, 0x30,        # Usage (X)
        0x09, 0x31,        # Usage (Y)
        0x09, 0x32,        # Usage (Z)
        0x81, 0x02,        # Input (Data, Variable, Absolute)
        0xC0               # End Collection
    ])

gamepad_descriptor = usb_hid.Device(
    report_descriptor=GAMEPAD_REPORT_DESCRIPTOR,
    usage_page=0x01,
    usage=0x05,
    report_ids=(1,),
    in_report_lengths=(3,),
    out_report_lengths=(0,)
)