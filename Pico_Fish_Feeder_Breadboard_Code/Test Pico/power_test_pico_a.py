from machine import I2C, Pin
from ina219 import INA219
import time
from time import sleep
import utime
import ssd1306



# Define I2C pins and OLED display address
I2C_SCL_PIN = 3
I2C_SDA_PIN = 2
I2C_FREQ = 400000
OLED_ADDR = 0x3c
# for blink
pin = Pin("LED", Pin.OUT)

# Initialize I2C object and OLED display object
i2c = I2C(1, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=OLED_ADDR)
# I2C Initialization (SDA: GP0, SCL: GP1)
i2cb = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# I2C-Scan - searching for connected Devices on the I2C Bus
devices = i2cb.scan()
if devices:
    print("I2C devices found:", [hex(device) for device in devices])
else:
    print("No I2C devices found. Check connections!")
    while True:
        pass


# INA219-Sensor Initialization
ina = INA219(i2cb)
ina.set_calibration_32V_1A()

# Clear OLED display
oled.fill(0)

# Display 'Hello World'
oled.text("Hello, world!", 0, 0)

# Push changes to the display
oled.show()


# main loop
while True:
    pin.toggle()
    
    try:
        current = ina.current
        voltage = ina.bus_voltage
        
        if current <= 0.05:
            current = 0
            
        if voltage <= 0.05:
            voltage = 0
            
        print("{:.2f} mA  {:.2f} V".format(current, voltage))
        utime.sleep_ms(250)
        
    except Exception as e:
        print("Error reading INA219:", e)
        
    sleep(1)