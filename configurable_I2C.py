import board
import busio


class ConfigurableI2C:
    def __init__(self, storagehelper):
        """
        Initialize the ConfigurableI2C class with a storage instance.
        :param storage: An instance of the Storage class.
        """
        self.storagehelper = storagehelper

    def initialize(self):
        """
        Initialize I2C pins based on settings in the storage.
        :return: An initialized I2C object or None if initialization is skipped.
        """
        # Read I2C configuration from settings
        config = self.storagehelper.read_from_file("settings.json")
        if not config:
            raise ValueError("Configuration is missing in the settings.")

        # Check if load cell is enabled and input type is "Loadcell"
        brake_config = config.get("brake", {})
        if not brake_config.get("on", False) or brake_config.get("input", {}).get("type") != "Loadcell":
            print("Load cell is disabled or not configured. Skipping I2C initialization.")
            return None

        i2c_config = config.get("i2c_config", {})
        if not i2c_config:
            raise ValueError("I2C configuration is missing in the settings.")

        # Retrieve SDA and SCL pins
        sda_pin_name = i2c_config.get("sda", "GP0")  # Default to GP0
        scl_pin_name = i2c_config.get("scl", "GP1")  # Default to GP1

        # Map pin names to actual board pins
        sda_pin = getattr(board, sda_pin_name, None)
        scl_pin = getattr(board, scl_pin_name, None)

        if not sda_pin or not scl_pin:
            raise ValueError(f"Invalid I2C pins: SDA={sda_pin_name}, SCL={scl_pin_name}")

        print(f"Initializing I2C with SDA={sda_pin_name}, SCL={scl_pin_name}")
        return busio.I2C(scl_pin, sda_pin)
