# main.py - MASTER (SENDER)

import network
import espnow
import time
import json
from machine import Pin, I2C
import dht

# Set up LED and DHT11 pin
led = Pin(2, Pin.OUT)      
sensor = dht.DHT11(Pin(32))  

def blink(duration = 500):
    led.value(1)
    time.sleep_ms(duration)
    led.value(0)

packet_id = 0   # number of the package

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

    # Packaging data    
    packet_id += 1
    timestamp = time.ticks_ms()
    data_send_json = {
        'id': packet_id,
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
    
    # Wait for the reply
    host, msg = e.recv(2000)
    
    if msg:
        blink()
        reply_ts = time.ticks_ms()
        delay = time.ticks_diff(reply_ts, timestamp)
        
        print(f' -> Reply from <{host.hex('-')}>: {msg.decode()}')
        print(f' -> Delay time: {delay}ms')
    elif host is None:
        print('No reply')
    
    print('-------------------------------------')
    time.sleep(2)


