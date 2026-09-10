from machine import UART, Pin
import time

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# Send a command or test string
uart.write("AT\r\n")  # if DA14531 firmware responds to AT commands

# Wait and read response
time.sleep(1)

if uart.any():
    response = uart.read().decode()
    print("Received from DA14531:", response)
else:
    print("No response from DA14531.")
    
while True:
    message = "Hello from Pico!\n"
    uart.write(message)
    print("Sent:", message)
    time.sleep(2)
