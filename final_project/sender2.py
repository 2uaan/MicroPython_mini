import network
import espnow
import time
import ujson
import esp32
from machine import Timer, Pin, ADC

nvs = esp32.NVS('my_system')
GATEWAY_MAC = b'\x14\x2B\x2F\xC5\xD8\x20'  

SENSOR_PIN = 34  # Chân Analog đọc độ ẩm
PUMP_PIN = 26     # Chân điều khiển Bơm (Relay/LED)

def save_channel(channel):
    try:
        nvs.set_i32('wifi_channel', channel)
        nvs.commit()
        print('Save wifi channel success!!')
    except:
        print('Save wifi channel failed!!')

def load_channel():
    try:
        ch = nvs.get_i32('wifi_channel')
        return ch
    except:
        return 100

# Giá trị hiệu chỉnh (Để tham khảo, việc tính % do Gateway lo)
# DRY_VAL = 2650
# WET_VAL = 800

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

e = espnow.ESPNow()
e.active(True)

send_channel = load_channel()

try:
    e.add_peer(GATEWAY_MAC)
except:
    pass

pump = Pin(PUMP_PIN, Pin.OUT)
adc = ADC(Pin(SENSOR_PIN))
adc.atten(ADC.ATTN_11DB) 
pump_state = False 

# Hàm nhận lệnh từ Gateway
# def recv_cb(e_obj):
#     global pump_state
#     while True:
#         mac, msg = e_obj.recv(0)
#         if mac is None: break
#         try:
#             data = ujson.loads(msg)
#             # Kiểm tra xem có lệnh bơm không
#             if 'pump' in data:
#                 new_state = data['pump']
#                 if new_state != pump_state:
#                     pump_state = new_state
#                     pump.value(1 if pump_state else 0)
#                     print(f"LỆNH BƠM TỪ GATEWAY: {'BẬT' if pump_state else 'TẮT'}")
#         except Exception as err:
#             print(f"Lỗi nhận lệnh: {err}")
# 
# e.irq(recv_cb)

def wait_for_toggle(timer):
    global led_state
    host, msg = e.recv(10)
    
    if msg:
        print(f'Received: {msg.decode()}')
        mess = msg.decode()
        mess_json = ujson.loads(mess)
        
        if (mess_json.get('pump') == '1'):
            blink()
            led_state = 1 - led_state
            led.value(led_state)
        
        recv_channel = int(mess_json.get('channel'))
        if (recv_channel != send_channel):
            send_channel = recv_channel
            save_channel(send_channel)
            wlan.config(channel = send_channel)
            
        
wait_toggle = Timer(0)
wait_toggle.init(period = 100, mode = Timer.PERIODIC, callback= wait_for_toggle)

# --- VÒNG LẶP CHÍNH ---
print("Node 1 Start...")
while True:
    hum_val = adc.read()
        
    msg = ujson.dumps({
        "id": 1,
        "hum": hum_val,
        "pump": pump_state
    })
    
    # 3. Gửi đi
    try:
        e.send(GATEWAY_MAC, msg)
        print(f"Gửi: {msg} | Bơm: {'ON' if pump_state else 'OFF'}")
    except Exception as err:
        print(f"Lỗi gửi: {err}")

    time.sleep(2)
