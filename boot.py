from simple.boot import gamepad_descriptor
import usb_hid
import supervisor
# import storage
# import board, digitalio

# button = digitalio.DigitalInOut(board.GP12)
# button.pull = digitalio.Pull.UP

# # Disable devices only if button is not pressed.
# if button.value:
#    storage.disable_usb_drive()

# pid 0x5050 = "BMW DTM M4"
# pid 0x5051 = "AUDI RS5 DTM"
# pid 0x5052 = "AUDI R8 LMS"
# pid 0x5053 = "AMG GT3"
# .. keep space for more steering wheels
# pid 0x5060 = "Pedalbox"

# Define custom VID, PID, product name, and manufacturer
CUSTOM_VID = 0xDDFD  # Non-registered VID
CUSTOM_PID = 0x5060  # Non-registered PID
PRODUCT_NAME = "PedalBox"
MANUFACTURER_NAME = "Custom Sim Hardware"

# Set USB identification
supervisor.set_usb_identification(vid=CUSTOM_VID, pid=CUSTOM_PID, manufacturer=MANUFACTURER_NAME, product=PRODUCT_NAME)


# Enable HID devices including the custom gamepad descriptor
usb_hid.enable(
    (usb_hid.Device.KEYBOARD,
     usb_hid.Device.MOUSE,
     usb_hid.Device.CONSUMER_CONTROL,
     gamepad_descriptor)
)

# Set interface name for the gamepad
usb_hid.set_interface_name("PedalBox")

# Only use the gamepad
usb_hid.enable((gamepad_descriptor,))