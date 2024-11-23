import os
import json

class UtilLib:
    def array_map_multiplier(self, arr, multiplier):
        """
        Multiply all elements in the array by the multiplier and return a new array.
        """
        return [int(val * multiplier) for val in arr]

    def copy_array(self, src, dst, length):
        """
        Copy elements from src to dst up to the specified length.
        """
        dst[:length] = src[:length]

    def generate_string_map(self, lst):
        """
        Generate a hyphen-separated string from the list.
        """
        return "-".join(map(str, lst))

    def generate_string_map_cali(self, lst):
        """
        Generate a hyphen-separated string from the first 4 elements of the list.
        """
        return "-".join(map(str, lst[:4]))

    def get_value(self, data, separator, index):
        """
        Split a string by the specified separator and return the value at the given index.
        """
        parts = data.split(separator)
        return parts[index] if 0 <= index < len(parts) else ""

    def scale_map(self, value, low_in, high_in, low_out, high_out):
        """
        Map a value from one range to another.
        """
        if high_in == low_in:
            raise ValueError("Input range cannot be zero.")
        return int((value - low_in) * (high_out - low_out) / (high_in - low_in) + low_out)

    def scale_multi_map(self, value, input_map, output_map):
        """
        Map a value using multiple ranges defined in input_map and output_map.
        """
        if len(input_map) != len(output_map):
            raise ValueError("Input and output maps must have the same length.")
        if value <= input_map[0]:
            return output_map[0]
        if value >= input_map[-1]:
            return output_map[-1]

        for i in range(len(input_map) - 1):
            if input_map[i] <= value <= input_map[i + 1]:
                return self.scale_map(
                    value, input_map[i], input_map[i + 1], output_map[i], output_map[i + 1]
                )

        return output_map[-1]
