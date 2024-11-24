import time
from UtilLibrary import UtilLib
import microcontroller
from Pedal import Pedal
from adafruit_ads1x15.ads1115 import ADS1115
from simple import Gamepad
from bit_utils import get_bit_depth
import usb_cdc
from gpio_utils import check_pinout
import usb_hid

utilLib = UtilLib()

# Constants
E_INIT = "init_flag"
E_PEDAL_INVERTED_MAP = "pedal_inverted_map"
E_PEDAL_SMOOTH_MAP = "pedal_smooth_map"


class Pedals:
    def __init__(self, i2c):
        self.i2c = i2c
        self.gamepad = Gamepad(usb_hid.devices)

        # Create the pedals
        self._throttle = Pedal("T:", self.i2c, self.gamepad)
        self._brake = Pedal("B:", self.i2c, self.gamepad)
        self._clutch = Pedal("C:", self.i2c, self.gamepad)

        self._pedals = {
            "throttle": {"pedal": self._throttle, "prefix": "T"},
            "brake": {"pedal": self._brake, "prefix": "B"},
            "clutch": {"pedal": self._clutch, "prefix": "C"},
        }
        self._on_states = {"throttle": False, "brake": False, "clutch": False}

    def setup(self):
        """
        Initialize the pedals, load settings, and configure ADS1115.
        """
        print("Setting up pedals...")
        self.load_settings()

        # Configure the ADS1115
        _ads1015 = ADS1115(self.i2c)
        _ads1015.gain = 0  # 6.144 volts
        _ads1015.mode = 0  # Continuous mode
        _ads1015.data_rate = 7  # Fast data rate

    def loop(self):
        try:
            rx, ry, rz = 0, 0, 0
            serial_string = ""

            # Process throttle pedal
            if self._on_states["throttle"]:
                self._throttle.read_values()
                new_rx = self._throttle.get_after_hid()
                if new_rx != rx:  # Only update if value has changed
                    rx = new_rx
                serial_string += self._throttle.get_pedal_string()

            # Process brake pedal
            if self._on_states["brake"]:
                self._brake.read_values()
                new_ry = self._brake.get_after_hid()
                if new_ry != ry:  # Only update if value has changed
                    ry = new_ry
                serial_string += self._brake.get_pedal_string()

            # Process clutch pedal
            if self._on_states["clutch"]:
                self._clutch.read_values()
                new_rz = self._clutch.get_after_hid()
                if new_rz != rz:  # Only update if value has changed
                    rz = new_rz
                serial_string += self._clutch.get_pedal_string()

            # Send HID report if any value has changed
            self.gamepad.set_axes(rx=rx, ry=ry, rz=rz)

            # Send serial output if available
            if usb_cdc.console.out_waiting == 0:
                usb_cdc.console.write(serial_string.encode("utf-8") + b"\n")
        except Exception as e:
            print(f"Unhandled exception in loop: {e}")



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
        print(f"Processing message: {msg}")
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
            print("Processing GetMap command")  # Debug line
            try:
                map_entries = []
                for name, pedal in self._pedals.items():
                    prefix = pedal["prefix"]
                    output_map = pedal["pedal"].get_output_map_values("", f"{name}_output_map")
                    map_entry = f"{prefix}MAP:{','.join(map(str, output_map))}"
                    map_entries.append(map_entry)

                map_values = ",".join(map_entries)
                print(f"Generated map values: {map_values}")  # Debug line
                usb_cdc.console.write(f"MAP:{map_values}\n".encode("utf-8"))
            except Exception as e:
                print(f"Error in get_map: {e}")  # Debug line




    def get_inverted(self, msg):
        """
        Send the inversion status of all pedals via serial in the format INVER:1-1-1.
        """
        if "GetInverted" in msg:
            print("Processing GetInverted command")  # Debug line
            try:
                inverted_values = []
                for pedal in self._pedals.values():
                    inverted_values.append(str(int(pedal["pedal"].get_inverted_values())))
                
                result = "-".join(inverted_values)
                print(f"Inverted values: {result}")  # Debug line
                usb_cdc.console.write(f"INVER:{result}\n".encode("utf-8"))
            except Exception as e:
                print(f"Error in get_inverted: {e}")  # Debug line


    def get_smooth(self, msg):
        """
        Send the smoothing status of all pedals via serial in the format SMOOTH:1-1-1.
        """
        if "GetSmooth" in msg:
            print("Processing GetSmooth command")  # Debug line
            try:
                smooth_values = []
                for pedal in self._pedals.values():
                    smooth_values.append(str(int(pedal["pedal"].get_smooth_values())))
                
                result = "-".join(smooth_values)
                print(f"Smoothing values: {result}")  # Debug line
                usb_cdc.console.write(f"SMOOTH:{result}\n".encode("utf-8"))
            except Exception as e:
                print(f"Error in get_smooth: {e}")  # Debug line



    def get_calibration(self, msg):
        """
        Send the calibration values of all pedals via serial using their prefixes.
        """
        if "GetCali" in msg:
            print("Processing GetCali command")  # Debug line
            try:
                calibration_entries = []
                for name, pedal in self._pedals.items():
                    prefix = pedal["prefix"]
                    calibration_values = pedal["pedal"].get_calibration_values(f"{prefix}CALI:")
                    calibration_entry = f"{prefix}CALI:{','.join(map(str, calibration_values))}"
                    calibration_entries.append(calibration_entry)

                result = ",".join(calibration_entries)
                print(f"Calibration values: {result}")  # Debug line
                usb_cdc.console.write(f"CALI:{result}\n".encode("utf-8"))
            except Exception as e:
                print(f"Error in get_calibration: {e}")  # Debug line


    def get_bits(self, msg):
        """
        Send the bit depths (raw and HID) of all pedals via serial.
        """
        if "GetBits" in msg:
            print("Processing GetBits command")  # Debug line
            try:
                bits_values = []
                for name in self._pedals.keys():
                    raw_bit = self._pedals[name]["pedal"]._raw_bit
                    hid_bit = self._pedals[name]["pedal"]._hid_bit
                    bits_values.append(f"{raw_bit}-{hid_bit}")

                result = "-".join(bits_values)
                print(f"Bit values: {result}")  # Debug line
                usb_cdc.console.write(f"BITS:{result}\n".encode("utf-8"))
            except Exception as e:
                print(f"Error in get_bits: {e}")  # Debug line


    def update_inverted(self, msg):
        """
        Update the inversion settings of all pedals based on the serial command.
        """
        if "INVER:" in msg:
            print(f"Processing INVER command: {msg}")  # Debug line
            try:
                split_inverted = utilLib.get_value(msg, ',', 0).replace("INVER:", "").split("-")
                for name, inverted in zip(self._pedals.keys(), split_inverted):
                    self._pedals[name]["pedal"].set_inverted_values(int(inverted))
                print(f"Updated inverted values: {split_inverted}")  # Debug line
            except Exception as e:
                print(f"Error in update_inverted: {e}")  # Debug line


    def update_smooth(self, msg):
        """
        Update the smoothing settings of all pedals based on the serial command.
        """
        if "SMOOTH:" in msg:
            print(f"Processing SMOOTH command: {msg}")  # Debug line
            try:
                split_smooth = utilLib.get_value(msg, ',', 0).replace("SMOOTH:", "").split("-")
                for name, smooth in zip(self._pedals.keys(), split_smooth):
                    self._pedals[name]["pedal"].set_smooth_values(int(smooth))
                print(f"Updated smoothing values: {split_smooth}")  # Debug line
            except Exception as e:
                print(f"Error in update_smooth: {e}")  # Debug line


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