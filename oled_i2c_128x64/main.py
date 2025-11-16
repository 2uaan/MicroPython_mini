# main.py - Chương trình kiểm tra OLED bằng thư viện

from machine import Pin, I2C
import time
import dht

dht_sensor = dht.DHT11(Pin(32))

# Thử import thư viện. Nếu thất bại, có thể bạn chưa cài
try:
    from ssd1306 import SSD1306_I2C
except ImportError:
    print("LỖI: Chưa cài thư viện 'micropython-ssd1306'")
    print("Hãy dùng Thonny > Tools > Manage packages... để cài đặt.")
    # Dừng chương trình nếu không có thư viện
    import sys
    sys.exit()

# --- CẤU HÌNH ---
OLED_WIDTH = 128
OLED_HEIGHT = 64

# ĐỊA CHỈ 7-BIT (Đây là mấu chốt!)
# Dùng 0x3C, KHÔNG DÙNG 0x78
OLED_ADDR = 0x3C 

# Chân I2C (SCL=22, SDA=21 là phổ biến)
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21

# --- KHỞI TẠO ---
print("Đang khởi tạo I2C...")
try:
    i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=400000)
    print("I2C đã khởi tạo.")
    
    # --- QUÉT I2C (Bước gỡ lỗi quan trọng) ---
    print("Đang quét bus I2C...")
    devices = i2c.scan()
    
    if not devices:
        print("LỖI: Không tìm thấy bất kỳ thiết bị I2C nào!")
        print("Kiểm tra lại dây cắm VCC, GND, SCL, SDA.")
    else:
        print("Các thiết bị I2C tìm thấy tại (dạng hex):", [hex(d) for d in devices])
        
        # Kiểm tra xem có thấy OLED không
        if OLED_ADDR not in devices:
            print(f"LỖI: Không tìm thấy OLED tại địa chỉ {hex(OLED_ADDR)}!")
            print(f"Bạn có chắc chắn địa chỉ là {hex(OLED_ADDR)}?")
            print("Một số màn hình có thể ở địa chỉ 0x3D.")

    # --- KHỞI TẠO OLED ---
    print("Đang khởi tạo màn hình OLED...")
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, OLED_ADDR)
    print("Khởi tạo OLED thành công.")
    
    count = 0
    temp_pre = 0
    hum_pre = 0
    while True:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
        except:
            print('Error when read from DHT11!!!')
            temp = 0
            hum = 0
        
        if temp_pre != temp or hum_pre != hum:
            oled.fill(0)
            oled.show()
            oled.text(f'Temp: {temp}C', 0, 0)
            oled.text(f'Hum: {hum}%',0 ,20)
            oled.show()
            
        temp_pre = temp
        hum_pre = hum
        time.sleep_ms(100)
        
    
    
    print("Test hoàn tất. Màn hình sẽ hiển thị chữ.")

except Exception as e:
    print(f"LỖI NGHIÊM TRỌNG: {e}")
    print("Vui lòng kiểm tra lại mọi thứ.")