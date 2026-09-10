from machine import I2C, Pin
import time

DS3231_ADDR = 0x68

# Registers
REG_SECONDS  = 0x00
REG_ALARM1   = 0x07
REG_CONTROL  = 0x0E
REG_STATUS   = 0x0F

def bcd2dec(bcd):
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def dec2bcd(dec):
    return ((dec // 10) << 4) | (dec % 10)

class DS3231:
    def __init__(self, i2c):
        self.i2c = i2c

    def get_time(self):
        """Returns (year, month, day, hour, minute, second)"""
        data = self.i2c.readfrom_mem(DS3231_ADDR, REG_SECONDS, 7)
        sec  = bcd2dec(data[0] & 0x7F)
        mn   = bcd2dec(data[1])
        hr   = bcd2dec(data[2] & 0x3F)
        day  = bcd2dec(data[4])
        mo   = bcd2dec(data[5] & 0x1F)
        yr   = bcd2dec(data[6]) + 2000
        return (yr, mo, day, hr, mn, sec)

    def set_time(self, year, month, day, hour, minute, second, weekday=0):
        """Set DS3231 time. weekday: 1=Mon, 7=Sun"""
        data = bytearray([
            dec2bcd(second),
            dec2bcd(minute),
            dec2bcd(hour),
            dec2bcd(weekday),
            dec2bcd(day),
            dec2bcd(month),
            dec2bcd(year - 2000)
        ])
        self.i2c.writeto_mem(DS3231_ADDR, REG_SECONDS, data)

    def set_alarm1_minutes_from_now(self, minutes):
        """Set Alarm 1 to fire X minutes from current DS3231 time."""
        yr, mo, day, hr, mn, sec = self.get_time()

        # Add minutes
        mn += minutes
        while mn >= 60:
            mn -= 60
            hr += 1
        hr = hr % 24

        # Alarm 1 registers: sec, min, hour, day
        # Set A1M4=1 (ignore day), A1M3=0, A1M2=0, A1M1=0
        # This matches when hour, minute, and second match
        alarm_data = bytearray([
            dec2bcd(0),           # second = 0
            dec2bcd(mn),          # minute
            dec2bcd(hr),          # hour
            0b10000000,           # day — ignored (A1M4 bit set)
        ])
        self.i2c.writeto_mem(DS3231_ADDR, REG_ALARM1, alarm_data)

        # Enable Alarm 1 interrupt, disable SQW output
        ctrl = self.i2c.readfrom_mem(DS3231_ADDR, REG_CONTROL, 1)[0]
        ctrl |= 0x05   # INTCN=1, A1IE=1
        ctrl &= ~0x18  # clear RS1, RS2
        self.i2c.writeto_mem(DS3231_ADDR, REG_CONTROL, bytearray([ctrl]))

        print(f"DS3231 alarm set for {hr:02d}:{mn:02d}:00")

    def clear_alarm1(self):
        """Clear Alarm 1 flag so SQW pin goes HIGH again."""
        status = self.i2c.readfrom_mem(DS3231_ADDR, REG_STATUS, 1)[0]
        status &= ~0x01  # clear A1F bit
        self.i2c.writeto_mem(DS3231_ADDR, REG_STATUS, bytearray([status]))
