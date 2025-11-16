# main.py - MASTER (SENDER)

import network
import espnow
import time
import json
from machine import Pin, I2C, Timer
import dht

# Set up LED and DHT11 pin
led = Pin(32, Pin.OUT)
led_state = 0
led.value(led_state)

led_onboard = Pin(2, Pin.OUT)      
sensor = dht.DHT11(Pin(23))  
led.value(0)

ID_NODE = 1

def blink(duration = 500):
    led_onboard.value(1)
    time.sleep_ms(duration)
    led_onboard.value(0)


# Set up network and ESP-NOW
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
e = espnow.ESPNow()
e.active(True)

# MAC address of Receiver
SLAVE_MAC_ADDRESS = b'\x14\x2B\x2F\xC5\xD8\x20' 

try:
    e.add_peer(SLAVE_MAC_ADDRESS)
    print(f'Added peer: {SLAVE_MAC_ADDRESS.hex('-')}')
except OSError as er:
    print(f'Error: {er}')
    
def wait_for_toggle(timer):
    global led_state
    host, msg = e.recv(10)
    
    if msg:
        blink()
        print(f'Received: {msg.decode()}')
        led_state = 1 - led_state
        led.value(led_state)

wait_toggle = Timer(0)
wait_toggle.init(period = 100, mode = Timer.PERIODIC, callback= wait_for_toggle)

    
while True:
    # Read data from DHT11
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print(f'Readed: temp<{temp}> - hum<{hum}>')
    except OSError as er:
        print('Error when read from DHT11!!')
        temp = 0
        hum = 0

    timestamp = time.ticks_ms()
    data_send_json = {
        'id': ID_NODE,
        'ts': timestamp,
        'temp': temp,
        'hum': hum
    }
    
    data_send = json.dumps(data_send_json) # Turn to json string
    data_bytes = data_send.encode()
    
    # Send data to SLAVE_MAC_ADDRESS
    try:
        e.send(SLAVE_MAC_ADDRESS, data_bytes)
        print(f'Sended: {data_send}')
        blink()
    except:
        print('Error when send data!!!')
        time.sleep(3)
        continue
    
    print('-------------------------------------')
    time.sleep(2)