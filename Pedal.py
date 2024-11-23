from storage import Storage
from Filters import Biquad, BiquadType
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_hid.gamepad import Gamepad
from adafruit_hx711.hx711 import HX711
from adafruit_hx711.analog_in import AnalogIn

# Initialize storage
storage = Storage()

# Filters for smoothing pedal inputs
_brakeFilter = Biquad(BiquadType.LOWPASS, 0.2, 0.5, 0.0)
_clutchFilter = Biquad(BiquadType.LOWPASS, 0.2, 0.5, 0.0)
_throttleFilter = Biquad(BiquadType.LOWPASS, 0.2, 0.5, 0.0)


class Pedal:
    def __init__(self, prefix, i2c, gamepad):
        self._prefix = prefix
        self._raw_bit = 65535
        self._hid_bit = 65535
        self._serial_range = 100
        self._afterHID = 0
        self._signal = None
        self._loadCell = None
        self._ads1015 = ADS1115(i2c)
        self._channel = None
        self._analogInput = None
        self._inverted = False
        self._smooth = False
        self._inputMap = [0, 20, 40, 60, 80, 100]
        self._outputMap = [0, 20, 40, 60, 80, 100]
        self._calibration = [0, self._raw_bit, 0, self._raw_bit]
        self._pedalString = ""
        self._gamepad = gamepad

        # Preload configuration from storage
        self.preload_cache()

    # Configuration methods
    def set_bits(self, rawBit, hidBit):
        self._raw_bit = rawBit
        self._hid_bit = hidBit

    def config_analog(self, analogInput):
        self._analogInput = analogInput
        self._signal = 0

    def config_load_cell(self, DOUT, CLK):
        if not self._loadCell:
            self._loadCell = HX711(DOUT, CLK)
            self._loadCell.set_scale(-7050.0)
            self._loadCell.tare(10)
        self._signal = 1

    def config_ads(self, channel):
        self._channel = channel
        self._signal = 2

    # Accessors for HID and string output
    def get_after_hid(self):
        return self._afterHID

    def get_pedal_string(self):
        return self._pedalString

    # Pedal processing
    def read_values(self):
        """
        Read raw values from the configured input source.
        """
        rawValue = 0

        if self._signal == 0 and self._analogInput:
            rawValue = self._analogInput.read()
        elif self._signal == 1 and self._loadCell:
            rawValue = max(min(self._loadCell.get_value(1), 16777215), 0)
        elif self._signal == 2 and self._channel is not None:
            rawValue = max(self._ads1015.read(self._channel), 0)
        else:
            raise ValueError("Invalid signal configuration or missing input.")

        self.update_pedal(rawValue)

    def update_pedal(self, rawValue):
        """
        Process the raw value, apply smoothing, inversion, mapping, and update HID outputs.
        """
        if self._smooth:
            filter_map = {"B:": _brakeFilter, "T:": _throttleFilter, "C:": _clutchFilter}
            filter_instance = filter_map.get(self._prefix)
            if filter_instance:
                rawValue = filter_instance.process(rawValue)

        if self._inverted:
            rawValue = self._raw_bit - rawValue

        lowDeadzone = max(self._calibration[0], self._calibration[2])
        topDeadzone = min(self._calibration[1], self._calibration[3])
        pedalOutput = max(min(rawValue, topDeadzone), lowDeadzone)

        # HID mapping
        inputMapHID = utilLib.array_map_multiplier(self._inputMap[:], (self._hid_bit / 100))
        outputMapHID = utilLib.array_map_multiplier(self._outputMap[:], (self._hid_bit / 100))

        beforeHID = utilLib.scale_map(pedalOutput, lowDeadzone, topDeadzone, 0, self._hid_bit)
        afterHID = utilLib.scale_multi_map(beforeHID, inputMapHID, outputMapHID)

        # Serial mapping
        beforeSerial = utilLib.scale_map(pedalOutput, lowDeadzone, topDeadzone, 0, self._serial_range)
        afterSerial = utilLib.scale_multi_map(beforeSerial, self._inputMap, self._outputMap)

        self._pedalString = f"{self._prefix}{beforeSerial};{afterSerial};{rawValue};{beforeHID},"
        self._afterHID = afterHID

        # Update gamepad HID
        self._gamepad.move_joystick(x=afterHID, y=0)

    # Calibration and Configuration Methods

    def preload_cache(self):
        """
        Preload frequently accessed settings like output map and calibration into memory.
        """
        stored_map = storage.read_from_settings(f"{self._prefix}_output_map")
        if stored_map:
            self._outputMap = [int(utilLib.get_value(stored_map, '-', i)) for i in range(6)]
        else:
            self._outputMap = [0, 20, 40, 60, 80, 100]

    def set_smooth_values(self, smoothValues):
        self._smooth = bool(smoothValues)
        storage.write_to_settings(f"{self._prefix}_smooth", self._smooth)

    def get_smooth_values(self):
        self._smooth = storage.read_from_settings(f"{self._prefix}_smooth") or False
        return self._smooth

    def set_inverted_values(self, invertedValues):
        self._inverted = bool(invertedValues)
        storage.write_to_settings(f"{self._prefix}_inverted", self._inverted)

    def get_inverted_values(self):
        self._inverted = storage.read_from_settings(f"{self._prefix}_inverted") or False
        return self._inverted

    def reset_calibration_values(self, EEPROMSpace):
        resetMap = [0, self._raw_bit, 0, self._raw_bit]
        self._calibration = resetMap
        storage.write_to_settings(EEPROMSpace, utilLib.generate_string_map_cali(resetMap))

    def get_eeprom_calibration_values(self, EEPROMSpace):
        EEPROM_Map = storage.read_from_settings(EEPROMSpace)
        if EEPROM_Map:
            self.set_calibration_values(EEPROM_Map, EEPROMSpace)

    def set_calibration_values(self, map, EEPROMSpace):
        self._calibration = [int(utilLib.get_value(map, '-', i)) for i in range(4)]
        storage.write_to_settings(EEPROMSpace, map)

    def get_calibration_values(self, prefix):
        return prefix + utilLib.generate_string_map_cali(self._calibration)

    def reset_output_map_values(self, EEPROMSpace):
        resetMap = [0, 20, 40, 60, 80, 100]
        self._outputMap = resetMap
        storage.write_to_settings(EEPROMSpace, utilLib.generate_string_map(resetMap))

    def set_output_map_values(self, map, EEPROMSpace):
        self._outputMap = [int(utilLib.get_value(map, '-', i)) for i in range(6)]
        storage.write_to_settings(EEPROMSpace, map)

    def get_output_map_values(self, prefix, EEPROMSpace):
        return prefix + utilLib.generate_string_map(self._outputMap)
