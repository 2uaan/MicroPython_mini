# main.py - Chương trình kiểm tra OLED bằng thư viện

from machine import Pin, I2C, deepsleep, RTC
import time
import network
import ntptime
import esp
import gc
from ssd1306 import SSD1306_I2C

esp.osdebug(None)
gc.collect()
ssid = '12B05'
password = '11111112'

OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_ADDR = 0x3C 

I2C_SCL_PIN = 22
I2C_SDA_PIN = 21

first_day = (2023, 1, 7, 0, 0, 0, 0, 0)
new_day = False

rtc = RTC()

def connect_wifi_settime():
    #Connect to Wi-Fi
    try:
        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(ssid, password)
        count = 15
        while station.isconnected() == False:
            print('.')
            time.sleep(1)
        print('Connect Wi-Fi success!!!')
    except:
        print('Error when connect to Wi-Fi:')
    
    #Set time
    if station.isconnected():
        try:
            ntptime.settime()
            print("Đồng bộ thời gian thành công!")
            rtc.memory(b'done wifi')
        except OSError as e:
            print("Lỗi đồng bộ thời gian:", e)

def count_num(num):
    count = 0
    while num > 0:
        num = num // 10
        count += 1
    return count
    
def run_clock():
    #Get VN Time
    utc_time = time.time()             
    vn_time = utc_time + 7 * 3600
    current_time = time.localtime(vn_time)
    time_str = f"{current_time[3]:02d}:{current_time[4]:02d}"
    second = current_time[5]
    
    #Calculate days
    count = (vn_time - time.mktime(first_day)) // (24 * 60 * 60)
    count_number = (128 - (count_num(count)*6 + (count_num(count)-1)*2)) // 2
    
    #Set up OLED
    i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=400000)
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, OLED_ADDR)
    
    #Display infor
    oled.text(f'{time_str}', 45, 4)
    oled.text('Zet', 53, 20)
    oled.text(f'{count}', count_number, 35)
    oled.text('Bun', 53, 50)
    oled.show()
    
    #Deepsleep
    deepsleep((60 - second)*1000)
    
if rtc.memory() != b'done wifi':
    connect_wifi_settime()
else:
    print("Thức dậy từ Deepsleep (Warm Boot).")    

run_clock()
    
    
    
    
