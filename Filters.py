# Filters.py

import math

class BiquadType:
    LOWPASS = 0
    HIGHPASS = 1
    BANDPASS = 2
    NOTCH = 3
    PEAK = 4
    LOWSHELF = 5
    HIGHSHELF = 6

class Biquad:
    def __init__(self, b_type, Fc, Q, peakGainDB):
        self.z1 = 0.0
        self.z2 = 0.0
        self.a0 = self.a1 = self.a2 = self.b1 = self.b2 = 0.0
        self.set_biquad(b_type, Fc, Q, peakGainDB)

    def set_biquad(self, b_type, Fc, Q, peakGainDB):
        self.type = b_type
        self.Fc = min(max(Fc, 0.0), 0.5)  # Constrain Fc between 0 and 0.5
        self.Q = Q
        self.peakGain = peakGainDB
        self.calc_biquad()

    def calc_biquad(self):
        self.z1 = 0.0
        self.z2 = 0.0
        V = math.pow(10, abs(self.peakGain) / 20.0)
        K = math.tan(math.pi * self.Fc)
        norm = 1

        if self.type == BiquadType.LOWPASS:
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = K * K * norm
            self.a1 = 2 * self.a0
            self.a2 = self.a0
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == BiquadType.HIGHPASS:
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = 1 * norm
            self.a1 = -2 * self.a0
            self.a2 = self.a0
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == BiquadType.BANDPASS:
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = K / self.Q * norm
            self.a1 = 0
            self.a2 = -self.a0
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == BiquadType.NOTCH:
            norm = 1 / (1 + K / self.Q + K * K)
            self.a0 = (1 + K * K) * norm
            self.a1 = 2 * (K * K - 1) * norm
            self.a2 = self.a0
            self.b1 = self.a1
            self.b2 = (1 - K / self.Q + K * K) * norm

        elif self.type == BiquadType.PEAK:
            if self.peakGain >= 0:  # Boost
                norm = 1 / (1 + 1 / self.Q * K + K * K)
                self.a0 = (1 + V / self.Q * K + K * K) * norm
                self.a1 = 2 * (K * K - 1) * norm
                self.a2 = (1 - V / self.Q * K + K * K) * norm
                self.b1 = self.a1
                self.b2 = (1 - 1 / self.Q * K + K * K) * norm
            else:  # Cut
                norm = 1 / (1 + V / self.Q * K + K * K)
                self.a0 = (1 + 1 / self.Q * K + K * K) * norm
                self.a1 = 2 * (K * K - 1) * norm
                self.a2 = (1 - 1 / self.Q * K + K * K) * norm
                self.b1 = self.a1
                self.b2 = (1 - V / self.Q * K + K * K) * norm

        elif self.type == BiquadType.LOWSHELF:
            norm = 1 / (1 + math.sqrt(2) * K + K * K)
            self.a0 = (1 + math.sqrt(2 * V) * K + V * K * K) * norm
            self.a1 = 2 * (V * K * K - 1) * norm
            self.a2 = (1 - math.sqrt(2 * V) * K + V * K * K) * norm
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - math.sqrt(2) * K + K * K) * norm

        elif self.type == BiquadType.HIGHSHELF:
            norm = 1 / (1 + math.sqrt(2) * K + K * K)
            self.a0 = (V + math.sqrt(2 * V) * K + K * K) * norm
            self.a1 = 2 * (K * K - V) * norm
            self.a2 = (V - math.sqrt(2 * V) * K + K * K) * norm
            self.b1 = 2 * (K * K - 1) * norm
            self.b2 = (1 - math.sqrt(2) * K + K * K) * norm

    def process(self, value):
        out = value * self.a0 + self.z1
        self.z1 = value * self.a1 + self.z2 - self.b1 * out
        self.z2 = value * self.a2 - self.b2 * out
        return out

# Example usage
# if __name__ == "__main__":
#     # Create a low-pass filter with a cutoff frequency of 0.1, Q factor of 0.707, and no peak gain
#     lowpass_filter = Biquad(BiquadType.LOWPASS, 0.1, 0.707, 0.0)

#     # Process a sample value through the filter
#     input_value = 1.0
#     output_value = lowpass_filter.process(input_value)
#     print(f"Filtered output: {output_value}")
