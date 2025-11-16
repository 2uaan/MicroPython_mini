# main.py - SLAVE (RECEIVER)

import network
import espnow
import time
import json
from machine import Pin, I2C
from lcd_api import I2C_LCD

#SET UP LCD & LED
I2C_ADDRESS = 0x27
SCL_PIN = Pin(21)
SDA_PIN = Pin(22)
i2c = I2C(0, scl = SCL_PIN, sda = SDA_PIN, freq = 400000)
lcd = I2C_LCD(i2c, I2C_ADDRESS)

led = Pin(2, Pin.OUT)
led.value(0)

def blink(duration = 500):
    led.value(1)
    time.sleep_ms(duration)
    led.value(0)

#Set up network and ESP-NOW
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
e = espnow.ESPNow()
e.active(True)
peer_list = set()

while True:
    host, msg = e.recv() # Wait for receive
    
    if msg:
        receive_ts = time.ticks_ms() # Time when data received
        blink()
        data_received = msg.decode()
        print(f'Received data')
        if host not in peer_list: # add the host If the sender MAC address isn't added 
            try:
                e.add_peer(host)
                peer_list.add(host)
                print(f'Added: {host.hex('-')}')
            except OSError as er:
                print('Error when add new peer: {er}')
                
        
        
        try:    
            data_json = json.loads(data_received)
            send_time = data_json.get('ts')
            delay_fromSend = time.ticks_diff(receive_ts, send_time)
            
            lcd.display_str(f'Id:{data_json.get('id')}, D:{delay_fromSend}ms     ', 0,0)
            lcd.display_str(f'T:{data_json.get('temp')}C, H:{data_json.get('hum')}%', 0,1)
            
            
            print(f'- JSON DETAIL FROM {host.hex('-')}: {msg.decode()}')
            print(f'=> id: {data_json.get('id')}')
            print(f'=> temp: {data_json.get('temp')}')
            print(f'=> hum: {data_json.get('hum')}')
            print(f'=> Delay from send time: {delay_fromSend}ms')
            reply = b'Ack_OK'
        except OSError as er:
            print(f'Error when translate Json: {er}')
            reply = b'Ack_ERROR'


    # Send reply back to Sender    
    try:
        e.send(host, reply) 
        print(f'Reply <{host.hex('-')}>: {reply.decode()}')
        blink()
    except OSError as er:
        print(f'Error when reply: {er}')    
    
    print('--------------------------------')
        
        