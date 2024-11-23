from Pedals import Pedals
import board
import busio

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Create Pedals instance
pedals = Pedals()

def setup():
    """
    Perform initial setup of the pedals, loading settings from storage.
    """
    pedals.setup()

def loop():
    """
    Main loop to process pedal inputs and handle serial communication.
    """
    pedals.loop()

# Perform setup
setup()

# Run the loop indefinitely
while True:
    loop()
