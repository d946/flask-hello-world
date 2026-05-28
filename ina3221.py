from micropython import const

_DEFAULT_ADDRESS = const(0x40)
#
# Registers and bits definitions
#

# Config register
_REG_CONFIG = const(0x00)

_RESET = const(0x8000)
_ENABLE_CH = (None, const(0x4000), const(0x2000), const(0x1000))  # default set

_AVERAGING_MASK = const(0x0E00)
_AVERAGING_NONE = const(0x0000)  # 1 sample, default
_AVERAGING_4_SAMPLES = const(0x0200)
_AVERAGING_16_SAMPLES = const(0x0400)
_AVERAGING_64_SAMPLES = const(0x0600)
_AVERAGING_128_SAMPLES = const(0x0800)
_AVERAGING_256_SAMPLES = const(0x0A00)
_AVERAGING_512_SAMPLES = const(0x0C00)
_AVERAGING_1024_SAMPLES = const(0x0E00)

_VBUS_CONV_TIME_MASK = const(0x01C0)
_VBUS_CONV_TIME_140US = const(0x0000)
_VBUS_CONV_TIME_204US = const(0x0040)
_VBUS_CONV_TIME_332US = const(0x0080)
_VBUS_CONV_TIME_588US = const(0x00C0)
_VBUS_CONV_TIME_1MS = const(0x0100)  # 1.1ms, default
_VBUS_CONV_TIME_2MS = const(0x0140)  # 2.116ms
_VBUS_CONV_TIME_4MS = const(0x0180)  # 4.156ms
_VBUS_CONV_TIME_8MS = const(0x01C0)  # 8.244ms

_SHUNT_CONV_TIME_MASK = const(0x0038)
_SHUNT_CONV_TIME_140US = const(0x0000)
_SHUNT_CONV_TIME_204US = const(0x0008)
_SHUNT_CONV_TIME_332US = const(0x0010)
_SHUNT_CONV_TIME_588US = const(0x0018)
_SHUNT_CONV_TIME_1MS = const(0x0020)  # 1.1ms, default
_SHUNT_CONV_TIME_2MS = const(0x0028)  # 2.116ms
_SHUNT_CONV_TIME_4MS = const(0x0030)  # 4.156ms
_SHUNT_CONV_TIME_8MS = const(0x0038)  # 8.244ms

_MODE_MASK = const(0x0007)
_MODE_POWER_DOWN = const(0x0000)  # Power-down
_MODE_SHUNT_VOLTAGE_TRIGGERED = const(0x0001)  # Shunt voltage, single-shot (triggered)
_MODE_BUS_VOLTAGE_TRIGGERED = const(0x0002)  # Bus voltage, single-shot (triggered)
_MODE_SHUNT_AND_BUS_TRIGGERED = const(0x0003)  # Shunt and bus, single-shot (triggered)
_MODE_POWER_DOWN2 = const(0x0004)  # Power-down
_MODE_SHUNT_VOLTAGE_CONTINUOUS = const(0x0005)  # Shunt voltage, continous
_MODE_BUS_VOLTAGE_CONTINUOUS = const(0x0006)  # Bus voltage, continuous
_MODE_SHUNT_AND_BUS_CONTINOUS = const(0x0007)  # Shunt and bus, continuous (default)

# Other registers
_REG_SHUNT_VOLTAGE = const(0x01)
_REG_SHUNT_VOLTAGE_CH = (None, const(0x01), const(0x03), const(0x05))
_REG_BUS_VOLTAGE = const(0x02)
_REG_BUS_VOLTAGE_CH = (None, const(0x02), const(0x04), const(0x06))
_REG_CRITICAL_ALERT_LIMIT_CH = (None, const(0x07), const(0x09), const(0x0B))
_REG_WARNING_ALERT_LIMIT_CH = (None, const(0x08), const(0x0A), const(0x0C))
_REG_SHUNT_VOLTAGE_SUM = const(0x0D)
_REG_SHUNT_VOLTAGE_SUM_LIMIT = const(0x0E)

# Mask/enable register
_REG_MASK_ENABLE = const(0x0F)
_SUM_CONTROL_CH = (None, const(0x4000), const(0x2000), const(0x1000))  # default not set
_WARNING_LATCH_ENABLE = const(0x0800)  # default not set
_CRITICAL_LATCH_ENABLE = const(0x0400)  # default not set
_CRITICAL_FLAG_CH = (None, const(0x0200), const(0x0100), const(0x0080))
_SUM_ALERT_FLAG = const(0x0040)
_WARNING_FLAG_CH = (None, const(0x0020), const(0x0010), const(0x0008))
_POWER_ALERT_FLAG = const(0x0004)
_TIMING_ALERT_FLAG = const(0x0002)
_CONV_READY_FLAG = const(0x0001)

# Other registers
_REG_POWER_VALID_UPPER_LIMIT = const(0x10)
_REG_POWER_VALID_LOWER_LIMIT = const(0x11)
_REG_MANUFACTURER_ID = const(0xFE)
_REG_DIE_ID = const(0xFF)

# Constants for manufacturer and device ID
_MANUFACTURER_ID = const(0x5449)  # "TI"
_DIE_ID = const(0x3220)


def _to_signed(num):
    if num > 0x7FFF:
        num -= 0x10000
    return num


class INA3221:
    """Driver for the INA226 current sensor"""

    # @staticmethod
    # def _to_signed(val):
    #     if val > 32767:
    #         return val - 65536
    #     return val

    # @staticmethod
    # def _to_unsigned(val):
    #     if val < 0:
    #         return val + 65536
    #     return val

    def __init__(self, i2c_device, addr=0x40):
        self.i2c_device = i2c_device
        self.i2c_addr = addr
        self.buf = bytearray(2)
        # self.set_calibration()

    def set_calibration(self):
        mask = _AVERAGING_MASK | _VBUS_CONV_TIME_MASK | _SHUNT_CONV_TIME_MASK | _MODE_MASK
        value = _AVERAGING_16_SAMPLES | _VBUS_CONV_TIME_1MS | _SHUNT_CONV_TIME_1MS | _MODE_SHUNT_AND_BUS_CONTINOUS
        self._update_register(_REG_CONFIG, mask, value)

    def _write_register(self, reg, value):
        self.buf[0] = (value >> 8) & 0xFF
        self.buf[1] = value & 0xFF
        self.i2c_device.writeto_mem(self.i2c_addr, reg, self.buf)

    def _read_register(self, reg):
        self.i2c_device.readfrom_mem_into(self.i2c_addr, reg & 0xFF, self.buf)
        value = (self.buf[0] << 8) | (self.buf[1])
        return value

    def _update_register(self, reg, mask, value):
        """Read-modify-write value in register"""
        regvalue = self._read_register(reg)
        regvalue &= ~mask
        value &= mask
        self._write_register(reg, regvalue | value)

    def shunt_voltage(self, channel=0):
        """Returns the channel's shunt voltage in mV"""
        # assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        value = _to_signed(self._read_register(_REG_SHUNT_VOLTAGE + channel * 2)) / 8
        # convert to volts - LSB = 40uV
        return (value * 0.04, value * 0.4)

    def bus_voltage(self, channel=0):
        """The bus voltage (between V- and GND) in Volts"""
        raw_voltage = _to_signed(self._read_register(_REG_BUS_VOLTAGE + channel * 2)) / 8
        return raw_voltage * 0.008

    def is_good(self):
        """"""
        a = self._read_register(_REG_MANUFACTURER_ID)
        b = self._read_register(_REG_DIE_ID)
        return (a == _MANUFACTURER_ID) and (b == _DIE_ID)
