from simple.boot import gamepad_descriptor
import usb_hid
import usb_cdc
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


# Set interface name for the gamepad
usb_hid.enable(gamepad_descriptor, boot_device=1)
usb_hid.set_interface_name("PedalBox")
usb_cdc.enable(console=True, data=True)