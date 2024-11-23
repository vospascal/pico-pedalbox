import storage
import usb_hid
from adafruit_hid.gamepad import Gamepad
import supervisor

# Enable USB HID devices for gamepad support
usb_hid.enable(
    (usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE, usb_hid.Device.GAMEPAD)
)

# Ensure device identification
supervisor.set_usb_identification(
    vid=0x1234, pid=0x5678, manufacturer="Custom Manufacturer", product="PedalBox"
)

# Optional: Disable USB storage if needed
storage.disable_usb_drive()

# Gamepad initialization
gamepad = Gamepad()
