from machine import Pin, I2C
from lcd_api import I2C_LCD
import network
import espnow
import time
import esp32

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
e = espnow.ESPNow()
e.active(True)

SSID = '12B05'
PASS = '11111112'
NODE2_MAC_ADDRESS = b'\x88\x57\x21\x69\xf0\x20'
NODE1_MAC_ADDRESS = b'\x5C\x01\x3B\x4B\x41\xCC'


I2C_ADDRESS = 0x27
SCL_PIN = Pin(21)
SDA_PIN = Pin(22)

i2c = I2C(0, scl = SCL_PIN, sda = SDA_PIN, freq = 400000)
lcd = I2C_LCD(i2c, I2C_ADDRESS)


original_channel = wlan.config('channel')
wifi_channel = 0
lcd.display_str(f'{original_channel}', 0,0)


wait = 15
if not wlan.isconnected():
    print('--Connet Wi-Fi--')
    wlan.connect(SSID, PASS)
    while not wlan.isconnected() and wait > 0:
        print('.')
        wait -= 1
        time.sleep(1)
    
if wlan.isconnected():
    wifi_channel = wlan.config('channel')
    lcd.display_str(f'{wifi_channel}', 0, 1)
else: lcd.display_str('Error', 0, 1)

try:
    e.add_peer(NODE1_MAC_ADDRESS)
    print('[ADD_PEER]: Node1 success!!')
    e.add_peer(NODE2_MAC_ADDRESS)
    print('[ADD_PEER]: Node2 success!!')
except:
    print('#*# Add new peer ERROR!!!')

wlan.disconnect()
wlan.config(channel = original_channel)
print(wlan.config('channel'))

while True:
    mess = f'{wifi_channel}'
    
    try:
        e.send(NODE1_MAC_ADDRESS, mess.encode())
        print(f'[DATA]: Send {mess} successed!!!')
    except:
        print('[ERROR]: Send {mess} failed!!')
        
    node, reply = e.recv(20)
    
    if reply:
        print(reply.decode())
        break
    else: print('No reply')
        
        
    time.sleep(1)

print('Channel data send success!!')
lcd.clear()

wait = 15
if not wlan.isconnected():
    print('--Reconnet Wi-Fi--')
    wlan.connect(SSID, PASS)
    while not wlan.isconnected() and wait > 0:
        print('.')
        wait -= 1
        time.sleep(1)

while True:
    node, data = e.recv(1000)
    
    if data:
        print(f'[DATA]: Received {data.decode()}')
        lcd.display_str(f'{data.decode()}', 0, 0)

    
