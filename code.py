from Pedals import Pedals
from configurable_I2C import ConfigurableI2C

# Create Pedals instance
class PedalController:
    def __init__(self):
        # Initialize Storage
        self.storagehelper = self.initialize_storage()

        # Configure and initialize I2C
        self.i2c = self.initialize_i2c()

        # Initialize Pedals with the configured I2C instance
        self.pedals = Pedals(self.i2c)
        self.setup()

    def initialize_storage(self):
        """
        Delayed import to avoid circular dependency.
        """
        from storage_helper import Storage_Helper
        return Storage_Helper()

    def initialize_i2c(self):
        """
        Use ConfigurableI2C to initialize I2C if needed.
        """
        try:
            configurable_i2c = ConfigurableI2C(self.storagehelper)
            return configurable_i2c.initialize()
        except ValueError as e:
            print(f"Skipping I2C initialization: {e}")
            return None

    def setup(self):
        """
        Perform initial setup of the pedals, loading settings from storage.
        """
        self.pedals.setup()

    def loop(self):
        """
        Main loop to process pedal inputs and handle serial communication.
        """
        self.pedals.loop()

    def run(self):
        while True:
            print("Entering loop...")
            self.loop()

if __name__ == "__main__":
    controller = PedalController()
    controller.run()