from machine import Pin
from time import sleep

class Led:
    def __init__(self, pin):
        self.led = Pin(pin, Pin.OUT)
        self.state = False

    def blink(self, time):
        self.change_state()
        sleep(time)
        self.change_state()
        sleep(time)

    def change_state(self):
        self.state = self.state == False
        if self.state: self.led.value(1)
        else: self.led.value(0)

def blink_3_led(l1, l2, l3, time):
    l1.change_state()
    l2.change_state()
    l3.change_state()
    sleep(time)
    l1.change_state()
    l2.change_state()
    l3.change_state()
    sleep(time)

class Button:
    def __init__(self, pin):
        self.bt = Pin(pin, Pin.IN)

    def get_value(self):
        return self.bt.value()



led1 = Led(14)
led2 = Led(27)
led3 = Led(26)
led4 = Led(25)
bt1 = Button(35)
bt2 = Button(34)

pre_bt1 = 0
pre_bt2 = 0

while True:
    if bt1.get_value() == 1 and pre_bt1 == 0:
        led1.change_state()
    if bt2.get_value() == 1 and pre_bt2 == 0:
        '''
        blink_3_led(led2, led3, led4, 0.5)
        blink_3_led(led2, led3, led4, 0.5)
        blink_3_led(led2, led3, led4, 0.5)
        '''
        led2.blink(0.5)
        led2.blink(0.5)
        led2.blink(0.5)
    pre_bt1 = bt1.get_value()
    pre_bt2 = bt2.get_value()

    sleep(0.1)
  

