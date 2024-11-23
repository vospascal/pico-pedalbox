# gpio_utils.py

import board

# Define a static map for GPIO pins with descriptions
GPIO_MAP = {
    0: {"board_pin": board.GP0, "description": "General Purpose"},
    1: {"board_pin": board.GP1, "description": "General Purpose"},
    2: {"board_pin": board.GP2, "description": "General Purpose"},
    3: {"board_pin": board.GP3, "description": "General Purpose"},
    4: {"board_pin": board.GP4, "description": "General Purpose"},
    5: {"board_pin": board.GP5, "description": "General Purpose"},
    6: {"board_pin": board.GP6, "description": "General Purpose"},
    7: {"board_pin": board.GP7, "description": "General Purpose"},
    8: {"board_pin": board.GP8, "description": "General Purpose"},
    9: {"board_pin": board.GP9, "description": "General Purpose"},
    10: {"board_pin": board.GP10, "description": "General Purpose"},
    11: {"board_pin": board.GP11, "description": "General Purpose"},
    12: {"board_pin": board.GP12, "description": "General Purpose"},
    13: {"board_pin": board.GP13, "description": "General Purpose"},
    14: {"board_pin": board.GP14, "description": "General Purpose"},
    15: {"board_pin": board.GP15, "description": "General Purpose"},
    16: {"board_pin": board.GP16, "description": "General Purpose"},
    17: {"board_pin": board.GP17, "description": "General Purpose"},
    18: {"board_pin": board.GP18, "description": "General Purpose"},
    19: {"board_pin": board.GP19, "description": "General Purpose"},
    20: {"board_pin": board.GP20, "description": "General Purpose"},
    21: {"board_pin": board.GP21, "description": "General Purpose"},
    22: {"board_pin": board.GP22, "description": "General Purpose"},
    23: {"board_pin": board.GP23, "description": "General Purpose"},
    24: {"board_pin": board.GP24, "description": "General Purpose"},
    25: {"board_pin": board.GP25, "description": "General Purpose"},
    26: {"board_pin": board.GP26, "description": "General Purpose"},
    27: {"board_pin": board.GP27, "description": "General Purpose"},
    28: {"board_pin": board.GP28, "description": "General Purpose"},
}

def check_pinout(settings):
    for pedal, config in settings.items():
        if "input" in config and "pin" in config["input"]:
            pin_number = config["input"]["pin"]
            pin_number = int(pin_number.replace("GP", "")) if "GP" in pin_number else None

            if pin_number in GPIO_MAP:
                expected_pin = GPIO_MAP[pin_number]["board_pin"]
                description = GPIO_MAP[pin_number]["description"]
                print(f"{pedal}: Using pin {expected_pin} ({description})")
            else:
                print(f"Warning: {pedal} is using an invalid or undefined GPIO pin: {config['input']['pin']}")