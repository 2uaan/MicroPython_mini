from machine import Pin, PWM, Timer
import time

led1 = PWM(Pin(32), freq=1000)   
led2 = Pin(33, Pin.OUT)
button = Pin(26, Pin.IN, Pin.PULL_DOWN)

# global
mode = 0
button_flag = False
log_flag = False
led_state = [0, 0]  # [LED1, LED2]
uptime_start = time.ticks_ms()
fade_direction = 1
duty_cycle = 0
last_press = 0

# set led1 value
def set_led1(brightness):
    led1.duty_u16(int(brightness))

set_led1(0)
led2.value(0)

#Button Interrupt
def button_isr(pin):
    global button_flag, last_press
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press) > 200: #do not press a button consecutively
        button_flag = True
        last_press = now

button.irq(trigger=Pin.IRQ_FALLING, handler=button_isr)

# timer 1
def blink_timer_isr(timer):
    global led_state, mode
    if mode == 0:
        set_led1(0)
        led_state[1] = 1 - led_state[1]
        led2.value(1 if led_state[1] else 0)
    elif mode == 1:
        led2.value(0)
        led_state[0] = 1 - led_state[0]
        set_led1(65535 if led_state[0] else 0)
    

blink_timer = Timer(0)
blink_timer.init(period=500, mode=Timer.PERIODIC, callback=blink_timer_isr)

def fade_led1(timer):
    global fade_direction, duty_cycle, led_state, mode
    if mode == 2:
        duty_cycle = duty_cycle + fade_direction * 512
        if duty_cycle >= 65535:
            fade_direction = -1
            duty_cycle = 65535
        elif duty_cycle <= 0:
            fade_direction = 1
            duty_cycle = 0
        
        set_led1(duty_cycle)
        led2.value(1)

        led_state = [duty_cycle, 1]

fade_timer = Timer(1)
fade_timer.init(period = 10, mode=Timer.PERIODIC, callback = fade_led1)



# timer 2
def log_timer_isr(timer):
    global log_flag
    log_flag = True

log_timer = Timer(2)
log_timer.init(period=5000, mode=Timer.PERIODIC, callback=log_timer_isr)

print("System started.")
while True:

    if button_flag:
        button_flag = False
        mode = (mode + 1) % 4
        print(f"Button pressed --> [MODE {mode}]")

        set_led1(0)
        led2.value(0)
        led_state = [0,0]
        time.sleep_ms(200)

    if log_flag:
        log_flag = False
        uptime = time.ticks_diff(time.ticks_ms(), uptime_start) // 1000
        print(f"<LOG> Mode[{mode}] - Uptime[{uptime}s] - led1[{led_state[0]}] - led2[{led_state[1]}]")

    if mode == 3:
        set_led1(65535)
        led2.value(1)
        led_state = [1,1]

    time.sleep_ms(50)

