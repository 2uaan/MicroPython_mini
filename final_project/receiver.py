# main.py - SLAVE (RECEIVER)

import network
import espnow
import time
import json
import machine
from machine import Pin, I2C
from lcd_api import I2C_LCD

#Set up BUTTON
button1 = Pin(32, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(33, Pin.IN, Pin.PULL_DOWN)
flag_button1 = False
flag_button2 = False
last_press1 = 0
last_press2 = 0 

#SET UP LCD & LED
I2C_ADDRESS = 0x27
SCL_PIN = Pin(21)
SDA_PIN = Pin(22)
i2c = I2C(0, scl = SCL_PIN, sda = SDA_PIN, freq = 400000)
lcd = I2C_LCD(i2c, I2C_ADDRESS)
lcd.display_str('----', 6,0)
lcd.display_str('----', 6,1)

DRY_VALUE = 3000
WET_VALUE = 1100
DISTANCE = DRY_VALUE - WET_VALUE


led = Pin(2, Pin.OUT)
led.value(0)

NODE2_MAC_ADDRESS = b'\x88\x57\x21\x69\xf0\x20'
NODE1_MAC_ADDRESS = b'\x5C\x01\x3B\x4B\x41\xCC'

def blink(duration = 200):
    led.value(1)
    time.sleep_ms(duration)
    led.value(0)

#Set up network and ESP-NOW
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
e = espnow.ESPNow()
e.active(True)

def adc_to_percent(adc):
    percent = (DISTANCE - adc + WET_VALUE) * 100 // DISTANCE
    return percent

try:
    e.add_peer(NODE1_MAC_ADDRESS)
    e.add_peer(NODE2_MAC_ADDRESS)
except:
    print('Error when add MAC address!!!')

#Interrupt for toggle LED
def led1(pin):
    global last_press1, flag_button1
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press1) > 200:
        flag_button1 = True

button1.irq(trigger= Pin.IRQ_FALLING, handler= led1)

def led2(pin):
    global last_press2, flag_button2
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press1) > 200:
        flag_button2 = True

button2.irq(trigger= Pin.IRQ_FALLING, handler= led2)


while True:
    host, msg = e.recv(10) # Wait for receive
    
    if msg:
#         receive_ts = time.ticks_ms()
        blink()
        data = msg.decode()
        data_json = json.loads(data)
#         delay_time = receive_ts - data_json.get('ts')
        
        
        if host == NODE1_MAC_ADDRESS:
            lcd.display_str(f'N1    H:{adc_to_percent(data_json.get('hum'))}%  ', 0, 0)
            print(f'Received from node 1: {data}')
#             print(f'Delay: {delay_time}')
            
        if host == NODE2_MAC_ADDRESS:
            lcd.display_str(f'N1 H:{adc_to_percent(data_json.get('hum'))}% ', 0, 1)
            print(f'Received from node 2: {data}')
#             print(f'Delay: {delay_time}')
    
#     irq_state = machine.disable_irq() 
#     if flag_button1:
#         flag_button1 = False # Hạ cờ ngay lập tức
#         machine.enable_irq(irq_state) 
#         print("-> Phat hien Nut 1! Dang gui lenh cho Sender 1...")
#         try:
#             e.send(NODE1_MAC_ADDRESS, b'change_LED_state')
#         except OSError as e:
#             print(f"Loi gui lenh cho S1: {e}")
# 
#     else:
#         machine.enable_irq(irq_state)
#         
#     irq_state = machine.disable_irq() 
#     if flag_button2:
#         flag_button2 = False # Hạ cờ ngay lập tức
#         machine.enable_irq(irq_state) 
#         print("-> Phat hien Nut 2! Dang gui lenh cho Sender 2...")
#         try:
#             e.send(NODE2_MAC_ADDRESS, b'change_LED_state')
#         except OSError as e:
#             print(f"Loi gui lenh cho S2: {e}")
# 
#     else:
#         machine.enable_irq(irq_state) 
          
        



