import ssd1306
import time
from time import sleep
from machine import Pin, I2C

# Define I2C pins and OLED display address
I2C_SCL_PIN = 9
I2C_SDA_PIN = 8
I2C_FREQ = 400000
OLED_ADDR = 0x3c
# for blink
pin = Pin("LED", Pin.OUT)

# Initialize I2C object and OLED display object
i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=OLED_ADDR)

# Clear OLED display
oled.fill(0)

# Display 'Hello World'
oled.text("Hello, world!", 0, 0)

# Push changes to the display
oled.show()

while True:
    pin.toggle()
    sleep(1)