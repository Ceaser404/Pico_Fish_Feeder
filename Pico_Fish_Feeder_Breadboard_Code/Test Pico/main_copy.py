from machine import Pin, I2C, deepsleep, reset_cause
import time
from ds3231 import DS3231

# ---- PINS ----
RELAY_PIN = 12
LED_PIN   = 25
SQW_PIN   = 15   # DS3231 SQW → Pico GP15

relay = Pin(RELAY_PIN, Pin.OUT)
led   = Pin(LED_PIN, Pin.OUT)

# I2C for DS3231 (SDA=GP0, SCL=GP1)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
ds  = DS3231(i2c)

# SQW pin — DS3231 pulls LOW on alarm
sqw = Pin(SQW_PIN, Pin.IN, Pin.PULL_UP)

# ---- CONFIG ----
SLEEP_MINUTES = 1   # how long to sleep between cycles
ON_SECONDS    = 10   # how long relay stays on

# ---- SET DS3231 TIME ONCE ----
# Uncomment, flash once, then comment out again:
ds.set_time(2026, 5, 9, 12, 0, 0)  # (year, month, day, hour, min, sec)

# ----------------------------------------------------------------
# Show reset cause via blinks:
#   2 blinks = fresh power on
#   3 blinks = woke from deepsleep
#   6 blinks = other reset
# ----------------------------------------------------------------
cause = reset_cause()
blinks = {0: 2, 3: 3}.get(cause, 6)  # 3 = deepsleep wake on Pico 2
for _ in range(blinks):
    led.value(1)
    time.sleep(0.2)
    led.value(0)
    time.sleep(0.2)
time.sleep(0.3)

print("Reset cause:", cause)
print("DS3231 time:", ds.get_time())

# ---- 2-second stop window (only needed during dev) ----
print("Starting in 2s — hit Stop to interrupt")
time.sleep(2)

# ---- ACTIVE PHASE ----
print("Relay and LED ON")
led.value(1)
relay.value(1)
time.sleep(ON_SECONDS)
relay.value(0)
led.value(0)
print("Relay and LED OFF")

# ---- SET ALARM AND SLEEP ----
ds.clear_alarm1()                               # clear any previous alarm flag
ds.set_alarm1_minutes_from_now(SLEEP_MINUTES)  # tell DS3231 when to wake

print("Entering deepsleep, SQW will wake on alarm...")
time.sleep(0.5)  # let print flush

# deepsleep with no timeout — wakes ONLY when SQW pin goes LOW
deepsleep()
# Pico resets on wake → main.py runs from top again
