from machine import Pin, ADC, PWM
import time
import network
import espnow
import json
from mg90s import MG90S

ID_NODE = 1 #Id number of node

#Set up LED, Servo, and HW-390 Pin
led = Pin(2, Pin.OUT)
st_led = 0
led.value(st_led)

servo = MG90S(pin_num=32)
servo.angle(0)

DRY_VALUE = 3000
WET_VALUE = 1100
DISTANCE = DRY_VALUE - WET_VALUE
ADC_PIN = Pin(34, Pin.IN, Pin.PULL_DOWN)
adc = ADC(ADC_PIN)

#Blink LED on-board
def blink_led():
    led.value(1)
    time.sleep(0.2)
    led.value(0)

#Convert from ADC value to angle of servo
def adc_to_angle(adc):
    percent = percent = (DISTANCE - adc + WET_VALUE) * 100 // DISTANCE
    angle = percent * 180 // 100
    return 180 - angle


#Set up ESP-NOW
RECEIVER_MAC_ADDRESS = b'\x14\x2B\x2F\xC5\xD8\x20' 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
e = espnow.ESPNow()
e.active(True)

try:
    e.add_peer(RECEIVER_MAC_ADDRESS)
    print('Add new peer success!!')
except:
    print('Add new peer error!!')


#Change to Wifi channel
wlan.config(channel = 11)
print(wlan.config('channel'))


#Send data loop
while True:
    hum = adc.read()
    data_json = {
        'id': ID_NODE,
        'hum': hum
    }
    servo.angle(adc_to_angle(hum))
    
    data = json.dumps(data_json)
    data_send = data.encode()
    
    try:
        e.send(RECEIVER_MAC_ADDRESS, data_send)
        print(f'Send data success: {data}')
        blink_led()
    except:
        print('Send data error!!')
    time.sleep(2)


