from UtilLibrary import UtilLib
import microcontroller
from Pedal import Pedal
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_hid.gamepad import Gamepad
import usb_cdc
import board
import busio

# Initialize I2C and Gamepad
i2c = busio.I2C(board.SCL, board.SDA)
gamepad = Gamepad()
utilLib = UtilLib()

# Constants
E_INIT = "init_flag"
E_PEDAL_KEYS = {
    "throttle": {
        "output_map": "throttle_output_map",
        "calibration": "throttle_calibration",
        "bits": "throttle_bits",
        "input": "throttle_input",
        "on": "throttle_on",
    },
    "brake": {
        "output_map": "brake_output_map",
        "calibration": "brake_calibration",
        "bits": "brake_bits",
        "input": "brake_input",
        "on": "brake_on",
    },
    "clutch": {
        "output_map": "clutch_output_map",
        "calibration": "clutch_calibration",
        "bits": "clutch_bits",
        "input": "clutch_input",
        "on": "clutch_on",
    },
}
E_PEDAL_INVERTED_MAP = "pedal_inverted_map"
E_PEDAL_SMOOTH_MAP = "pedal_smooth_map"

# Create the pedals
_throttle = Pedal("T:", i2c, gamepad)
_brake = Pedal("B:", i2c, gamepad)
_clutch = Pedal("C:", i2c, gamepad)


class Pedals:
    def __init__(self):
        self._pedals = {"throttle": _throttle, "brake": _brake, "clutch": _clutch}
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

    def process_serial_command(self, msg):
        """
        Process incoming serial commands.
        """
        if "clearEEPROM" in msg:
            self.clear_eeprom()
            usb_cdc.console.write(b"done\n")

        self.reset_device()
        self.handle_command(msg, "GetUsage", self.get_usage)
        self.handle_command(msg, "GetMap", self.get_map)
        self.handle_command(msg, "GetInverted", self.get_inverted)
        self.handle_command(msg, "GetSmooth", self.get_smooth)
        self.handle_command(msg, "GetCali", self.get_calibration)
        self.handle_command(msg, "GetBits", self.get_bits)

        for pedal_name, key in E_PEDAL_KEYS.items():
            if f"{pedal_name.upper()}MAP:" in msg:
                map_value = msg.replace(f"{pedal_name.upper()}MAP:", "")
                self._pedals[pedal_name].set_output_map_values(map_value, key["output_map"])

        if "CALIRESET" in msg:
            for pedal_name, key in E_PEDAL_KEYS.items():
                self._pedals[pedal_name].reset_calibration_values(key["calibration"])

        if all(k in msg for k in ["CCALI:", "BCALI:", "TCALI:"]):
            for pedal_name, prefix in {"throttle": "TCALI", "brake": "BCALI", "clutch": "CCALI"}.items():
                cali_value = utilLib.get_value(msg, ",", 0).replace(f"{prefix}:", "")
                self._pedals[pedal_name].set_calibration_values(cali_value, E_PEDAL_KEYS[pedal_name]["calibration"])


    def reset_device(self, msg):
        """
        Reboot the device if the RESET command is received.
        """
        if "RESET" in msg:
            print("Resetting device...")
            self.reset_device_settings()

    def load_settings(self):
        """
        Load all settings from storage. If the device has not been initialized, reset all settings to defaults.
        """
        initialized = utilLib.read_from_storage(E_INIT)

        if initialized:
            for name, key in E_PEDAL_KEYS.items():
                pedal = self._pedals[name]
                pedal.get_output_map_values("", key["output_map"])
                pedal.get_eeprom_calibration_values(key["calibration"])

            inverted_map = utilLib.read_from_storage(E_PEDAL_INVERTED_MAP) or "0-0-0"
            self.update_inverted(f"INVER:{inverted_map}")

            smooth_map = utilLib.read_from_storage(E_PEDAL_SMOOTH_MAP) or "1-1-1"
            self.update_smooth(f"SMOOTH:{smooth_map}")
        else:
            self.reset_device_settings()
            

    def reset_device_settings(self):
        """
        Reset all pedal-related settings to defaults and reboot the device.
        """
        utilLib.write_to_storage(E_INIT, True)
        for name, key in E_PEDAL_KEYS.items():
            pedal = self._pedals[name]
            pedal.reset_output_map_values(key["output_map"])
            pedal.reset_calibration_values(key["calibration"])
        utilLib.write_to_storage(E_PEDAL_INVERTED_MAP, "0-0-0")
        utilLib.write_to_storage(E_PEDAL_SMOOTH_MAP, "1-1-1")

        time.sleep(1)
        microcontroller.reset()

    def handle_command(self, msg, command, handler):
        """
        Helper method to process serial commands.
        """
        if command in msg:
            handler(msg)

    def clear_eeprom(self):
        """Clear all settings from storage."""
        utilLib.clear_storage()

    # Helper methods for serial commands
    def get_usage(self, msg):
        if "GetUsage" in msg:
            usage = f"USAGE:{self._throttle_on}-{self._brake_on}-{self._clutch_on}"
            usb_cdc.console.write(usage.encode('utf-8') + b'\n')

    def get_map(self, msg):
        if "GetMap" in msg:
            map_values = (
                _throttle.get_output_map_values("TMAP:") + "," +
                _brake.get_output_map_values("BMAP:") + "," +
                _clutch.get_output_map_values("CMAP:")
            )
            usb_cdc.console.write(map_values.encode('utf-8') + b'\n')

    def get_inverted(self, msg):
        if "GetInverted" in msg:
            inverted_values = (
                f"INVER:{_throttle.get_inverted_values()}-{_brake.get_inverted_values()}-{_clutch.get_inverted_values()}"
            )
            usb_cdc.console.write(inverted_values.encode('utf-8') + b'\n')

    def get_smooth(self, msg):
        if "GetSmooth" in msg:
            smooth_values = (
                f"SMOOTH:{_throttle.get_smooth_values()}-{_brake.get_smooth_values()}-{_clutch.get_smooth_values()}"
            )
            usb_cdc.console.write(smooth_values.encode('utf-8') + b'\n')

    def get_calibration(self, msg):
        if "GetCali" in msg:
            calibration_values = (
                _throttle.get_calibration_values("TCALI:") + "," +
                _brake.get_calibration_values("BCALI:") + "," +
                _clutch.get_calibration_values("CCALI:")
            )
            usb_cdc.console.write(calibration_values.encode('utf-8') + b'\n')

    def update_inverted(self, msg):
        if "INVER:" in msg:
            split_inverted = utilLib.get_value(msg, ',', 0).replace("INVER:", "")
            _throttle.set_inverted_values(int(utilLib.get_value(split_inverted, '-', 0)))
            _brake.set_inverted_values(int(utilLib.get_value(split_inverted, '-', 1)))
            _clutch.set_inverted_values(int(utilLib.get_value(split_inverted, '-', 2)))

    def update_smooth(self, msg):
        if "SMOOTH:" in msg:
            split_smooth = utilLib.get_value(msg, ',', 0).replace("SMOOTH:", "")
            _throttle.set_smooth_values(int(utilLib.get_value(split_smooth, '-', 0)))
            _brake.set_smooth_values(int(utilLib.get_value(split_smooth, '-', 1)))
            _clutch.set_smooth_values(int(utilLib.get_value(split_smooth, '-', 2)))

    def get_bits(self, msg):
        if "GetBits" in msg:
            bits_values = (
                f"BITS:{self._throttle_raw_bit}-{self._throttle_hid_bit}-"
                f"{self._brake_raw_bit}-{self._brake_hid_bit}-"
                f"{self._clutch_raw_bit}-{self._clutch_hid_bit}"
            )
            usb_cdc.console.write(bits_values.encode('utf-8') + b'\n')


    def set_throttle_on(self, on):
        self._throttle_on = on
        utilLib.write_to_storage("throttle_on", on)

    def set_throttle_bits(self, rawBit, hidBit):
        self._throttle_raw_bit = self.get_bit(rawBit)
        self._throttle_hid_bit = self.get_bit(hidBit)
        utilLib.write_to_storage("throttle_bits", {"raw": rawBit, "hid": hidBit})

    def set_throttle_analog_pin(self, analogInput):
        self._throttle_pedalType = "Analog"
        self._throttle_analog_input = analogInput
        _throttle.config_analog(analogInput)
        utilLib.write_to_storage("throttle_input", {"type": "Analog", "pin": str(analogInput)})

    def set_brake_on(self, on):
        self._brake_on = on
        utilLib.write_to_storage("brake_on", on)

    def set_brake_bits(self, rawBit, hidBit):
        self._brake_raw_bit = self.get_bit(rawBit)
        self._brake_hid_bit = self.get_bit(hidBit)
        utilLib.write_to_storage("brake_bits", {"raw": rawBit, "hid": hidBit})

    def set_brake_loadcell(self, DOUT, CLK):
        self._brake_pedalType = "Loadcell"
        _brake.config_load_cell(DOUT, CLK)
        utilLib.write_to_storage("brake_input", {"type": "Loadcell", "pins": {"DOUT": DOUT, "CLK": CLK}})

    def set_clutch_on(self, on):
        self._clutch_on = on
        utilLib.write_to_storage("clutch_on", on)

    def set_clutch_bits(self, rawBit, hidBit):
        self._clutch_raw_bit = self.get_bit(rawBit)
        self._clutch_hid_bit = self.get_bit(hidBit)
        utilLib.write_to_storage("clutch_bits", {"raw": rawBit, "hid": hidBit})

    def set_clutch_analog_pin(self, analogInput):
        self._clutch_pedalType = "Analog"
        self._clutch_analog_input = analogInput
        _clutch.config_analog(analogInput)
        utilLib.write_to_storage("clutch_input", {"type": "Analog", "pin": str(analogInput)})
