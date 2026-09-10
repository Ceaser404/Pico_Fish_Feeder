from machine import Pin, I2C, lightsleep, reset_cause
import time
from ds3231 import DS3231

# ---- PINS ----
RELAY_PIN = 12
LED_PIN   = 25
SQW_PIN   = 15   # DS3231 SQW → Pico GP15 (physical pin 20)

relay = Pin(RELAY_PIN, Pin.OUT)
led   = Pin(LED_PIN, Pin.OUT)

# I2C for DS3231 (SDA=GP0, SCL=GP1)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
ds  = DS3231(i2c)

# SQW pin — DS3231 pulls LOW on alarm
sqw = Pin(SQW_PIN, Pin.IN, Pin.PULL_UP)

# ---- CONFIG ----
SLEEP_MINUTES = 1379  # how long to sleep between cycles
ON_SECONDS    = 50  # how long relay stays on

# ---- SET DS3231 TIME ONCE ----
# Uncomment, flash once, then comment out again:
# ds.set_time(2026, 5, 9, 12, 0, 0)  # (year, month, day, hour, min, sec)

# ---- WAKE HANDLER (needed for lightsleep pin wake) ----
woken = False
def wake_handler(pin):
    global woken
    woken = True

# ---- SAFETY BLINK ----
for _ in range(6):
    led.value(1)
    time.sleep(0.15)
    led.value(0)
    time.sleep(0.15)

print("Reset cause:", reset_cause())
print("DS3231 time:", ds.get_time())

# ---- 2-second stop window ----
print("Starting in 2s — hit Stop to interrupt")
time.sleep(2)

# ---- MAIN LOOP ----
while True:
    # Clear any previous alarm flag — ensures SQW is HIGH before sleeping
    ds.clear_alarm1()
    print("SQW state after clear:", sqw.value())  # should be 1

    # ---- ACTIVE PHASE ----
    print("Relay and LED ON")
    led.value(1)
    relay.value(1)
    time.sleep(ON_SECONDS)
    relay.value(0)
    led.value(0)
    print("Relay and LED OFF")

    # ---- SET NEXT ALARM ----
    ds.set_alarm1_minutes_from_now(SLEEP_MINUTES)
    print("DS3231 time now:", ds.get_time())

    # ---- LIGHTSLEEP UNTIL SQW GOES LOW ----
    woken = False
    sqw.irq(trigger=Pin.IRQ_FALLING, handler=wake_handler)
    print("Entering lightsleep...")
    time.sleep(0.1)  # let print flush

    while not woken:
        lightsleep(10000)  # sleep in 10s chunks, wakes on SQW or timeout

    print("Woke from lightsleep!")
    sqw.irq(handler=None)  # disable IRQ until next sleep cycle
