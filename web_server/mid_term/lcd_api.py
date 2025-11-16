from machine import I2C
import time

MODE_CMD = 0
MODE_DATA = 1

class I2C_LCD:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self.backlight = 0x08
        
        self.send_to_lcd(0x33, MODE_CMD) # 1) Gửi 0011 ba lần
        self.send_to_lcd(0x32, MODE_CMD) # 2) để chắc chắn vào chế độ 8-bit
        self.send_to_lcd(0x28, MODE_CMD) # 3) Function Set: 4-bit, 2 dòng, font 5x8
        self.send_to_lcd(0x0C, MODE_CMD) # 4) Display ON, con trỏ OFF
        self.send_to_lcd(0x06, MODE_CMD) # 5) Entry Mode Set: tự động tăng con trỏ
        self.clear()                     # 6) Xóa màn hình

    def toggle_enable(self, data):
        time.sleep_us(1)
        self.i2c.writeto(self.addr, bytes([data | 0x04])) # E=1
        time.sleep_us(1)
        self.i2c.writeto(self.addr, bytes([data & ~0x04])) # E=0
        time.sleep_us(50)

    def send_to_lcd(self, data, mode):
        high_nibble = (data & 0xF0) | mode | self.backlight
        self.toggle_enable(high_nibble)
            
        low_nibble = ((data << 4) & 0xF0) | mode | self.backlight
        self.toggle_enable(low_nibble)


    def clear(self):
        self.send_to_lcd(0x01, MODE_CMD)
        time.sleep_ms(2) 

    def move_to(self, col, row):
        if row == 0:
            addr = 0x80 + col
        elif row == 1:
            addr = 0xC0 + col
        else:
            return
        self.send_to_lcd(addr, MODE_CMD)
        
    def putstr(self, text):
        for char in text:
            self.send_to_lcd(ord(char), MODE_DATA)
