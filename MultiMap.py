# multi_map.py

def multi_map(val, in_list, out_list):
    """
    Maps a value from one range to another using non-linear mapping.
    
    :param val: The input value to map.
    :param in_list: A list of input values (must be increasing).
    :param out_list: A list of output values corresponding to in_list.
    :return: The mapped output value.
    """
    if len(in_list) != len(out_list):
        raise ValueError("Input and output lists must have the same length.")
    
    # Ensure the value is within the range
    if val <= in_list[0]:
        return out_list[0]
    if val >= in_list[-1]:
        return out_list[-1]

    # Search for the right interval
    pos = 1
    while val > in_list[pos]:
        pos += 1

    # Handle exact points in the in_list
    if val == in_list[pos]:
        return out_list[pos]

    # Interpolate in the right segment
    return (val - in_list[pos - 1]) * (out_list[pos] - out_list[pos - 1]) / (in_list[pos] - in_list[pos - 1]) + out_list[pos - 1]

#  Example usage
#  if __name__ == "__main__":
    #  in_values = [0, 10, 20, 30, 40, 50]
    #  out_values = [0, 100, 200, 300, 400, 500]
    #  value = 25
    #  mapped_value = multi_map(value, in_values, out_values)
    #  print(f"Mapped value: {mapped_value}")
