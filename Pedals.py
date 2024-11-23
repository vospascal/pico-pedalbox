from UtilLibrary import UtilLib
import microcontroller
from Pedal import Pedal
from adafruit_ads1x15.ads1115 import ADS1115
from simple import Gamepad
from bit_utils import get_bit_depth
import usb_cdc
import board
import busio
from gpio_utils import check_pinout

# Initialize I2C and Gamepad
i2c = busio.I2C(board.SCL, board.SDA)
gamepad = Gamepad()
utilLib = UtilLib()

# Constants
E_INIT = "init_flag"
E_PEDAL_INVERTED_MAP = "pedal_inverted_map"
E_PEDAL_SMOOTH_MAP = "pedal_smooth_map"

# Create the pedals
_throttle = Pedal("T:", i2c, gamepad)
_brake = Pedal("B:", i2c, gamepad)
_clutch = Pedal("C:", i2c, gamepad)


class Pedals:
    def __init__(self):
        self._pedals = {
            "throttle": {"pedal": _throttle, "prefix": "T"},
            "brake": {"pedal": _brake, "prefix": "B"},
            "clutch": {"pedal": _clutch, "prefix": "C"},
        }
        self._on_states = {"throttle": False, "brake": False, "clutch": False}

    def setup(self):
        """
        Initialize the pedals, load settings, and configure ADS1115.
        """
        self.load_settings()

        # Configure the ADS1115
        _ads1015 = ADS1115(i2c)
        _ads1015.gain = 0  # 6.144 volts
        _ads1015.mode = 0  # Continuous mode
        _ads1015.data_rate = 7  # Fast data rate

    def loop(self):
        """
        Main loop to handle serial commands and update pedals.
        """
        if usb_cdc.console.in_waiting > 0:
            try:
                msg = usb_cdc.console.readline().decode("utf-8").strip()
                self.process_serial_command(msg)
            except UnicodeDecodeError as e:
                print(f"Error decoding serial data: {e}")

        serial_string = ""
        for name, pedal in self._pedals.items():
            if self._on_states[name]:
                pedal.read_values()
                axis = {"throttle": "x", "brake": "y", "clutch": "z"}[name]
                gamepad.move_joystick(**{axis: pedal.get_after_hid()})
                serial_string += pedal.get_pedal_string()

        # Send HID state to the PC
        gamepad.send_report()

        if usb_cdc.console.out_waiting == 0:
            usb_cdc.console.write(serial_string.encode("utf-8") + b"\n")


    ### Serial Command Processing ###
    def process_serial_command(self, msg):
        """
        Process incoming serial commands.
        """
        if "clearEEPROM" in msg:
            self.clear_eeprom()
            usb_cdc.console.write(b"done\n")
        if "RESET" in msg:
            self.reset_device_settings()

        # Handle specific commands
        self.handle_command(msg, "GetUsage", self.get_usage)
        self.handle_command(msg, "GetMap", self.get_map)
        self.handle_command(msg, "GetInverted", self.get_inverted)
        self.handle_command(msg, "GetSmooth", self.get_smooth)
        self.handle_command(msg, "GetCali", self.get_calibration)
        self.handle_command(msg, "GetBits", self.get_bits)

    # Helper methods for serial commands
    def handle_command(self, msg, command, handler):
        """
        Helper method to process serial commands.
        """
        if command in msg:
            handler(msg)

    def clear_eeprom(self):
        """Clear all settings from storage."""
        utilLib.clear_storage()

    def get_usage(self, msg):
        """
        Send the usage status of all pedals via serial.
        """
        if "GetUsage" in msg:
            usage = ",".join([f"{name}:{self.get_pedal_on(name)}" for name in self._pedals.keys()])
            usb_cdc.console.write(f"USAGE:{usage}\n".encode("utf-8"))


    def get_map(self, msg):
        """
        Send the output map of all pedals via serial using their prefixes.
        """
        if "GetMap" in msg:
            map_values = ",".join(
                [
                    f"{pedal['prefix']}MAP:{','.join(map(str, pedal['pedal'].get_output_map_values('', f'{name}_output_map')))}"
                    for name, pedal in self._pedals.items()
                ]
            )
            usb_cdc.console.write(f"MAP:{map_values}\n".encode("utf-8"))



    def get_inverted(self, msg):
        """
        Send the inversion status of all pedals via serial in the format INVER:1-1-1.
        """
        if "GetInverted" in msg:
            inverted_values = "-".join(
                [str(int(pedal["pedal"].get_inverted_values())) for pedal in self._pedals.values()]
            )
            usb_cdc.console.write(f"INVER:{inverted_values}\n".encode("utf-8"))

    def get_smooth(self, msg):
        """
        Send the smoothing status of all pedals via serial in the format SMOOTH:1-1-1.
        """
        if "GetSmooth" in msg:
            smooth_values = "-".join(
                [str(int(pedal["pedal"].get_smooth_values())) for pedal in self._pedals.values()]
            )
            usb_cdc.console.write(f"SMOOTH:{smooth_values}\n".encode("utf-8"))


    def get_calibration(self, msg):
        """
        Send the calibration values of all pedals via serial using their prefixes.
        """
        if "GetCali" in msg:
            calibration_values = ",".join(
                [
                    f"{pedal['prefix']}CALI:{','.join(map(str, pedal['pedal'].get_calibration_values(f'{pedal['prefix']}CALI:')))}"
                    for name, pedal in self._pedals.items()
                ]
            )
            usb_cdc.console.write(f"CALI:{calibration_values}\n".encode("utf-8"))

    def get_bits(self, msg):
        """
        Send the bit depths (raw and HID) of all pedals via serial in the format:
        BITS:{raw_throttle}-{hid_throttle}-{raw_brake}-{hid_brake}-{raw_clutch}-{hid_clutch}.
        """
        if "GetBits" in msg:
            bits_values = "-".join(
                [
                    f"{self._pedals[name]['pedal']._raw_bit}-{self._pedals[name]['pedal']._hid_bit}"
                    for name in self._pedals.keys()
                ]
            )
            usb_cdc.console.write(f"BITS:{bits_values}\n".encode("utf-8"))

    def update_inverted(self, msg):
        """
        Update the inversion settings of all pedals based on the serial command.
        """
        if "INVER:" in msg:
            split_inverted = utilLib.get_value(msg, ',', 0).replace("INVER:", "").split("-")
            for name, inverted in zip(self._pedals.keys(), split_inverted):
                self._pedals[name].set_inverted_values(int(inverted))


    def update_smooth(self, msg):
        """
        Update the smoothing settings of all pedals based on the serial command.
        """
        if "SMOOTH:" in msg:
            split_smooth = utilLib.get_value(msg, ',', 0).replace("SMOOTH:", "").split("-")
            for name, smooth in zip(self._pedals.keys(), split_smooth):
                self._pedals[name].set_smooth_values(int(smooth))






    ### Generic Getter and Setter Methods ###
    def set_pedal_on(self, pedal_name, on):
        """
        Set the on/off state for a pedal.
        """
        self._on_states[pedal_name] = on
        utilLib.write_to_settings(f"{pedal_name}.on", on)

    def get_pedal_on(self, pedal_name):
        """
        Retrieve the on/off state for a pedal.
        """
        return utilLib.read_from_settings(f"{pedal_name}.on") or False

    def set_pedal_bits(self, pedal_name):
        """
        Set the raw and HID bit depths for a pedal using values from settings.
        """
        pedal = self._pedals[pedal_name]
        bits = utilLib.read_from_settings(pedal_name).get("bits", {})
        raw_bit = get_bit_depth(bits.get("raw", "16bit"))
        hid_bit = get_bit_depth(bits.get("hid", "16bit"))
        pedal.set_bits(raw_bit, hid_bit)
        utilLib.write_to_settings(f"{pedal_name}.bits", {"raw": raw_bit, "hid": hid_bit})

    def get_pedal_bits(self, pedal_name):
        """
        Retrieve the raw and HID bit depths for a pedal.
        """
        bits = utilLib.read_from_settings(pedal_name).get("bits", {})
        raw_bit = get_bit_depth(bits.get("raw", "16bit"))
        hid_bit = get_bit_depth(bits.get("hid", "16bit"))
        return raw_bit, hid_bit

    def set_pedal_input(self, pedal_name, input_type, **kwargs):
        """
        Set the input configuration for a pedal.
        :param pedal_name: The pedal name (e.g., "throttle").
        :param input_type: The type of input (e.g., "Analog", "Loadcell").
        :param kwargs: Additional configuration details (e.g., pin or DOUT/CLK pins).
        """
        pedal = self._pedals[pedal_name]
        if input_type == "Analog":
            pedal.config_analog(kwargs.get("pin"))
            utilLib.write_to_settings(f"{pedal_name}.input", {"type": "Analog", "pin": kwargs["pin"]})
        elif input_type == "Loadcell":
            pedal.config_load_cell(kwargs["DOUT"], kwargs["CLK"])
            utilLib.write_to_settings(f"{pedal_name}.input", {"type": "Loadcell", "pins": {"DOUT": kwargs["DOUT"], "CLK": kwargs["CLK"]}})

    def get_pedal_input(self, pedal_name):
        """
        Retrieve the input configuration for a pedal.
        """
        return utilLib.read_from_settings(f"{pedal_name}.input")

    ### Configuration Loading ###
    def load_settings(self):
        """
        Load all settings from storage. If the device has not been initialized, reset all settings to defaults.
        """
        initialized = utilLib.read_from_settings(E_INIT)
        if initialized:
            for name in self._pedals.keys():
                self.set_pedal_on(name, self.get_pedal_on(name))
                self.set_pedal_bits(name)
                input_config = self.get_pedal_input(name)
                if input_config:
                    if input_config["type"] == "Analog":
                        self.set_pedal_input(name, "Analog", pin=input_config["pin"])
                    elif input_config["type"] == "Loadcell":
                        pins = input_config["pins"]
                        self.set_pedal_input(name, "Loadcell", DOUT=pins["DOUT"], CLK=pins["CLK"])
            # Apply global inversion and smoothing settings
            self.update_inverted(f"INVER:{utilLib.read_from_settings(E_PEDAL_INVERTED_MAP)}")
            self.update_smooth(f"SMOOTH:{utilLib.read_from_settings(E_PEDAL_SMOOTH_MAP)}")

            # Validate pinout configuration
            settings = utilLib.read_from_settings()
            if settings:
                check_pinout(settings)
            else:
                print("Warning: No settings available to validate pinout.")
        else:
            self.reset_device_settings()

    ### Device Reset ###
    def reset_device_settings(self):
        """
        Reset all pedal-related settings to defaults and reboot the device.
        """
        utilLib.write_to_storage(E_INIT, True)
        for name in self._pedals.keys():
            pedal = self._pedals[name]
            pedal.reset_output_map_values(f"{name}_output_map")
            pedal.reset_calibration_values(f"{name}_calibration")
        utilLib.write_to_settings(E_PEDAL_INVERTED_MAP, "0-0-0")
        utilLib.write_to_settings(E_PEDAL_SMOOTH_MAP, "1-1-1")
        print("Resetting device...")
        time.sleep(1)
        microcontroller.reset()