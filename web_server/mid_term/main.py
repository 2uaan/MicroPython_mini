# main.py
from machine import Pin, I2C, Timer
import machine
import esp32
import dht
import time
import ntptime
import urequests
import json
from lcd_api import I2C_LCD
try:
  	  import usocket as socket
except:
  	  import socket
import network
import esp
import gc

#Firebase URL
FIREBASE_URL = 'https://esp32-dht11-5f8bc-default-rtdb.asia-southeast1.firebasedatabase.app/'

#Cau hinh Wi-Fi
esp.osdebug(None)
gc.collect()
ssid = '2uaan'
password = '22222888'
station = network.WLAN(network.STA_IF)

#Cau hinh Led
led = Pin(2, Pin.OUT)
led.value(1)
mode = 1
state = 1

#Cau hinh I2C LCD
i2c = I2C(0, scl=Pin(21), sda=Pin(22), freq=400000)
lcd = I2C_LCD(i2c, 0x27)

#Cau hinh DHT11 pin
dht_pin = machine.Pin(14)
sensor = dht.DHT11(dht_pin)

def read_dht11():
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()        
    except OSError as e:
        lcd.putstr("Loi doc DHT11")
        temp, hum = 0, 0
    return temp, hum

def sync_time():
    try:
        ntptime.settime()
        print("Đồng bộ thời gian thành công!")
    except OSError as e:
        print("Lỗi đồng bộ thời gian:", e)

def get_vietnam_time():
    utc_time = time.time()              #Lấy giờ UTC sau đó +7 để thành giờ Việt Nam
    vn_time = utc_time + (7 * 3600)
    return time.localtime(vn_time)

def send_to_firebase(temp, hum):
    current_time = get_vietnam_time()
    timestamp_str = f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
    pushID_key = f"Send_at_{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"  #Lấy time để tạo nhãn

    data_payload = {                #Đóng gói
        'nhiet do(do C)': temp,
        'do am(%)': hum,
        'timedate': timestamp_str
    }
    
    url = f"{FIREBASE_URL}/dht11_log/{pushID_key}.json"
    
    try:
        response = urequests.put(url, json=data_payload)        #Gửi dữ liệu lên Firebase theo url, sử dụng PUT
        print(f"Firebase response code: {response.status_code}")
        response.close()            #Đóng sau khi thực hiện xong
        return True
    except OSError as e:
        print("Lỗi khi gửi dữ liệu:", e)
        return False

def go_to_sleep():
    #Dậy khi nhấn nút
    button = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
    esp32.wake_on_ext1(pins=(button,), level=esp32.WAKEUP_ALL_LOW)
    
    #Dậy mỗi 30s
    sleep_duration_ms = 30000 
    print(f"Sẽ tỉnh dậy sau {sleep_duration_ms / 1000} giây hoặc khi nút được nhấn.")
    machine.deepsleep(sleep_duration_ms) #sleep

#Timer nháy LED
def blink_timer(timer):
    global mode, state
    if mode == 1:
        state = 1 - state
        led.value(1 if state else 0)
    elif mode == 0: led.value(1)

blink = Timer(0)
blink.init(period = 200, mode = Timer.PERIODIC, callback = blink_timer)

def main():
    global lcd, sensor, station,led, mode, state
    lcd.move_to(0, 1)
    lcd.putstr("S: WK")
    lcd.move_to(0, 0)

    #Hiển thị dữ liên lên LCD
    temp, hum = read_dht11()
    str_data = f"T: {temp}C H: {hum}%"
    lcd.putstr(str_data)
    

    station.active(True)
    station.connect(ssid, password)

    lcd.move_to(5, 1)
    connection_timeout = 10 # Chờ tối đa 10 giây
    while station.isconnected() == False and connection_timeout > 0:
        lcd.putstr(".")
        time.sleep(1)
        connection_timeout -= 1
    lcd.move_to(5,1)
    lcd.putstr("           ")

    if station.isconnected():
        print("Đã kết nối Wi-Fi!")
        # 4. Đồng bộ thời gian
        sync_time()
        
        mode = 0
        send_to_firebase(temp, hum)
    else:
        lcd.move_to(0, 1)
        lcd.putstr("S: WIFI FAILED")
        time.sleep(3) # Hiển thị lỗi trong 3 giây

    mode = 2
    for i in range(5):              #Nháy (1s) 3 lần trước khi vào trạng thái Deep Sleep
        state = 1 - state
        led.value(1 if state else 0)
        time.sleep_ms(1000)

    lcd.move_to(0, 1)
    lcd.putstr("S: DS         ")
    lcd.move_to(0, 1)
    go_to_sleep()
     

main()

