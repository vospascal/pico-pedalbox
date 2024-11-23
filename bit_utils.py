BIT_DEPTH_MAP = {
    "8bit": 255,
    "9bit": 511,
    "10bit": 1023,
    "11bit": 2047,
    "12bit": 4095,
    "13bit": 8191,
    "14bit": 16383,
    "15bit": 32767,
    "16bit": 65535,
    "17bit": 131071,
    "18bit": 262143,
    "19bit": 524287,
    "20bit": 1048575,
    "21bit": 2097151,
    "22bit": 4194303,
    "23bit": 8388607,
    "24bit": 16777215,
}

def get_bit_depth(bit_label):
    """
    Get the numeric value for a given bit-depth label.
    :param bit_label: A string like "10bit", "15bit", etc.
    :return: The corresponding numeric value, or 65535 if the label is invalid.
    """
    return BIT_DEPTH_MAP.get(bit_label, 65535)
