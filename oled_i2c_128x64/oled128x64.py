# Tệp: oled_driver.py

from machine import I2C

# Địa chỉ I2C mặc định
DEFAULT_ADDR = 0x3C

# Các lệnh cơ bản của SSD1306 (từ datasheet)
CMD_DISPLAY_OFF = 0xAE
CMD_DISPLAY_ON = 0xAF
CMD_SET_CHARGE_PUMP = 0x8D
CMD_SET_MEM_ADDR_MODE = 0x20
CMD_SET_DISPLAY_CLOCK_DIV = 0xD5
CMD_SET_MULTIPLEX = 0xA8
CMD_SET_DISPLAY_OFFSET = 0xD3
CMD_SET_START_LINE = 0x40
CMD_SET_SEGMENT_REMAP_1 = 0xA1 # Đảo cột
CMD_SET_COM_SCAN_DEC = 0xC8    # Đảo hàng
CMD_SET_CONTRAST = 0x81
CMD_ENTIRE_DISPLAY_ON_RESUME = 0xA4
CMD_SET_NORMAL_DISPLAY = 0xA6

class OLED_128_64:
    
    def __init__(self, i2c, addr=DEFAULT_ADDR, width=128, height=64):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        self.pages = self.height // 8
        
        # --- 1. TẠO FRAME BUFFER ---
        # Đây là "bức tranh" trong RAM của ESP32.
        # Kích thước: 128 cột * (64 hàng / 8 hàng_mỗi_page) = 1024 byte
        self.buffer = bytearray(self.width * self.pages)
        
        # --- 2. KHỞI TẠO MÀN HÌNH ---
        self.init_display()

    def _send_command(self, cmd):
        """Gửi một byte Lệnh (Command)"""
        buffer = bytearray(2)
        buffer[0] = 0x00 # Control Byte (0x00 = Command)
        buffer[1] = cmd
        self.i2c.writeto(self.addr, buffer)

    def _send_data(self, data_buffer):
        """Gửi một buffer Dữ liệu (Data)"""
        # Tạo một buffer mới với Control Byte 0x40 ở đầu
        # và theo sau là toàn bộ data_buffer
        buffer_with_control = bytearray(len(data_buffer) + 1)
        buffer_with_control[0] = 0x40 # Control Byte (0x40 = Data)
        buffer_with_control[1:] = data_buffer
        
        self.i2c.writeto(self.addr, buffer_with_control)

    def init_display(self):
        """Gửi chuỗi lệnh khởi tạo màn hình"""
        self._send_command(CMD_DISPLAY_OFF)
        self._send_command(CMD_SET_DISPLAY_CLOCK_DIV)
        self._send_command(0x80)
        self._send_command(CMD_SET_MULTIPLEX)
        self._send_command(self.height - 1)
        self._send_command(CMD_SET_DISPLAY_OFFSET)
        self._send_command(0x00)
        self._send_command(CMD_SET_START_LINE | 0x00)
        self._send_command(CMD_SET_CHARGE_PUMP)
        self._send_command(0x14) # Bật charge pump
        self._send_command(CMD_SET_MEM_ADDR_MODE)
        self._send_command(0x00) # Chế độ Horizontal Addressing
        self._send_command(CMD_SET_SEGMENT_REMAP_1)
        self._send_command(CMD_SET_COM_SCAN_DEC)
        self._send_command(0xDA) # (COM Pins Hardware Configuration, bỏ qua)
        self._send_command(0x12)
        self._send_command(CMD_SET_CONTRAST)
        self._send_command(0xCF)
        self._send_command(0xD9) # (Pre-charge Period)
        self._send_command(0xF1)
        self._send_command(0xDB) # (VCOMH Deselect Level)
        self._send_command(0x40)
        self._send_command(CMD_ENTIRE_DISPLAY_ON_RESUME)
        self._send_command(CMD_SET_NORMAL_DISPLAY)
        self._send_command(CMD_DISPLAY_ON)
        
        # Xóa buffer và màn hình khi khởi tạo
        self.clear()
        self.show()

    # ---------------------------------------------------
    # --- CÁC HÀM VẼ (TÁC ĐỘNG LÊN BUFFER TRONG RAM) ---
    # ---------------------------------------------------

    def fill(self, color):
        """
        Làm đầy toàn bộ buffer với 1 màu (0=TẮT, 1=BẬT)
        Đây chính là hàm "sáng toàn màn hình" hoặc "xóa toàn màn hình".
        """
        fill_byte = 0xFF if color else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = fill_byte

    def clear(self):
        """Hàm tiện ích: Xóa toàn bộ buffer (tắt hết pixel)"""
        self.fill(0)

    def pixel(self, x, y, color):
        """
        Bật/tắt một pixel tại tọa độ (x, y) trong buffer
        color (0=TẮT, 1=BẬT)
        """
        # Kiểm tra biên
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
            
        # 1. Tìm vị trí byte trong buffer:
        # Bộ nhớ được chia theo Page (8 pixel dọc).
        # (y // 8) -> Tìm đúng Page (0-7)
        # (y // 8) * self.width -> Nhảy đến đầu Page đó
        # ... + x -> Di chuyển đến đúng cột 'x'
        index = (y // 8) * self.width + x
        
        # 2. Tìm đúng bit trong byte đó:
        # (y % 8) -> Tìm vị trí bit trong cột 8 pixel (0-7)
        bit_mask = 1 << (y % 8)
        
        # 3. Sửa đổi buffer
        if color:
            # Bật bit (OR)
            self.buffer[index] = self.buffer[index] | bit_mask
        else:
            # Tắt bit (AND với NOT)
            self.buffer[index] = self.buffer[index] & ~bit_mask

    # ---------------------------------------------------
    # --- HÀM CẬP NHẬT (ĐẨY BUFFER LÊN MÀN HÌNH) ---
    # ---------------------------------------------------

    def show(self):
        """
        Đẩy toàn bộ Frame Buffer (1024 byte) từ RAM của ESP32 
        lên màn hình OLED.
        """
        # Gửi 3 lệnh để đặt con trỏ về đầu (Page 0, Column 0)
        self._send_command(0x21) # Lệnh Set Column Address
        self._send_command(0)    # Cột bắt đầu (0)
        self._send_command(self.width - 1) # Cột kết thúc (127)
        
        self._send_command(0x22) # Lệnh Set Page Address
        self._send_command(0)    # Page bắt đầu (0)
        self._send_command(self.pages - 1) # Page kết thúc (7)
        
        # Gửi toàn bộ 1024 byte buffer
        self._send_data(self.buffer)