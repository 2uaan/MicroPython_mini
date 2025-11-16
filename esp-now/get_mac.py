import network
import ubinascii

# Kích hoạt giao diện Wi-Fi Station
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

# Lấy địa chỉ MAC
mac = sta_if.config('mac')
mac_str = ubinascii.hexlify(mac, ':').decode('utf-8')

print("-----------------------------------")
print(f"Board MAC Address: {mac_str}")
print("-----------------------------------")

# Bạn có thể tắt Wi-Fi sau khi lấy MAC nếu muốn
# sta_if.active(False)
