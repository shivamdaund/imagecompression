class ArithmeticEncoder:
    def __init__(self, precision):
        self.low = 0
        self.high = (1 << precision) - 1
        self.precision = precision
        self.total_bits = []

    def encode(self, data, freq_table):
        total = sum(freq_table)
        cum_freq = [0]
        for freq in freq_table:
            cum_freq.append(cum_freq[-1] + freq)

        for symbol in data:
            range_size = self.high - self.low + 1
            self.high = self.low + (range_size * cum_freq[symbol + 1]) // total - 1
            self.low = self.low + (range_size * cum_freq[symbol]) // total

            while True:
                if self.high < (1 << (self.precision - 1)):
                    self.total_bits.append(0)
                    self.low <<= 1
                    self.high = (self.high << 1) | 1
                elif self.low >= (1 << (self.precision - 1)):
                    self.total_bits.append(1)
                    self.low = (self.low - (1 << (self.precision - 1))) << 1
                    self.high = ((self.high - (1 << (self.precision - 1))) << 1) | 1
                else:
                    break

        self.total_bits.append(1)

    def get_encoded_bits(self):
        return self.total_bits


class ArithmeticDecoder:
    def __init__(self, precision):
        self.low = 0
        self.high = (1 << precision) - 1
        self.precision = precision
        self.value = 0

    def decode(self, encoded_bits, length, freq_table):
        total = sum(freq_table)
        cum_freq = [0]
        for freq in freq_table:
            cum_freq.append(cum_freq[-1] + freq)

        for bit in encoded_bits[:self.precision]:
            self.value = (self.value << 1) | bit

        decoded_data = []
        for _ in range(length):
            range_size = self.high - self.low + 1
            cumulative = ((self.value - self.low + 1) * total - 1) // range_size
            for symbol, (low, high) in enumerate(zip(cum_freq[:-1], cum_freq[1:])):
                if low <= cumulative < high:
                    decoded_data.append(symbol)
                    self.high = self.low + (range_size * high) // total - 1
                    self.low = self.low + (range_size * low) // total
                    break

            while True:
                if self.high < (1 << (self.precision - 1)):
                    self.low <<= 1
                    self.high = (self.high << 1) | 1
                    self.value = (self.value << 1) & ((1 << self.precision) - 1)
                elif self.low >= (1 << (self.precision - 1)):
                    self.low = (self.low - (1 << (self.precision - 1))) << 1
                    self.high = ((self.high - (1 << (self.precision - 1))) << 1) | 1
                    self.value = ((self.value - (1 << (self.precision - 1))) << 1) & ((1 << self.precision) - 1)
                else:
                    break

        return decoded_data
