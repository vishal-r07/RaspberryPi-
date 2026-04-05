from machine import Pin, ADC
from time import sleep

# -------- LCD1 (RAW) --------
rs1 = Pin(0, Pin.OUT)
e1  = Pin(1, Pin.OUT)
d41 = Pin(2, Pin.OUT)
d51 = Pin(3, Pin.OUT)
d61 = Pin(4, Pin.OUT)
d71 = Pin(5, Pin.OUT)

# -------- LCD2 (ENCODED) --------
rs2 = Pin(6, Pin.OUT)
e2  = Pin(7, Pin.OUT)
d42 = Pin(8, Pin.OUT)
d52 = Pin(9, Pin.OUT)
d62 = Pin(10, Pin.OUT)
d72 = Pin(11, Pin.OUT)

# -------- POTENTIOMETERS --------
adc_speed = ADC(26)
adc_temp  = ADC(27)
adc_fuel  = ADC(28)

# -------- LCD FUNCTIONS --------
def pulse(e):
    e.value(1)
    sleep(0.001)
    e.value(0)
    sleep(0.001)

def send4(d4,d5,d6,d7,e,bits):
    d4.value((bits >> 0) & 1)
    d5.value((bits >> 1) & 1)
    d6.value((bits >> 2) & 1)
    d7.value((bits >> 3) & 1)
    pulse(e)

def send(rs,d4,d5,d6,d7,e,cmd,mode=0):
    rs.value(mode)
    send4(d4,d5,d6,d7,e,cmd >> 4)
    send4(d4,d5,d6,d7,e,cmd & 0x0F)
    sleep(0.002)

def lcd_init(rs,d4,d5,d6,d7,e):
    sleep(0.02)
    send(rs,d4,d5,d6,d7,e,0x33)
    send(rs,d4,d5,d6,d7,e,0x32)
    send(rs,d4,d5,d6,d7,e,0x28)
    send(rs,d4,d5,d6,d7,e,0x0C)
    send(rs,d4,d5,d6,d7,e,0x06)
    send(rs,d4,d5,d6,d7,e,0x01)
    sleep(0.002)

def write(rs,d4,d5,d6,d7,e,msg):
    for c in msg:
        send(rs,d4,d5,d6,d7,e,ord(c),1)

def set_cursor(rs,d4,d5,d6,d7,e,col,row):
    addr = 0x80 + col if row == 0 else 0xC0 + col
    send(rs,d4,d5,d6,d7,e,addr)

# INIT both LCDs
lcd_init(rs1,d41,d51,d61,d71,e1)
lcd_init(rs2,d42,d52,d62,d72,e2)

# -------- MAP FUNCTION --------
def map_value(x, in_min, in_max, out_min, out_max):
    return int((x - in_min)*(out_max-out_min)/(in_max-in_min)+out_min)

# -------- MAIN LOOP --------
while True:

    speed = map_value(adc_speed.read_u16(),0,65535,0,200)
    temp  = map_value(adc_temp.read_u16(),0,65535,20,120)
    fuel  = map_value(adc_fuel.read_u16(),0,65535,0,100)

    # -------- ENCODING --------
    D0 = int(speed*255/200)
    D1 = int(temp*255/120)
    D2 = int(fuel*255/100)

    CAN_ID = "0CF00400"

    # -------- LCD1 (RAW) --------
    set_cursor(rs1,d41,d51,d61,d71,e1,0,0)
    write(rs1,d41,d51,d61,d71,e1,"S:{} T:{}     ".format(speed,temp))

    set_cursor(rs1,d41,d51,d61,d71,e1,0,1)
    write(rs1,d41,d51,d61,d71,e1,"F:{}%         ".format(fuel))

    # -------- LCD2 (ENCODED) --------
    set_cursor(rs2,d42,d52,d62,d72,e2,0,0)
    write(rs2,d42,d52,d62,d72,e2,"ID:"+CAN_ID[:8])

    set_cursor(rs2,d42,d52,d62,d72,e2,0,1)
    write(rs2,d42,d52,d62,d72,e2,"{:02X} {:02X} {:02X}".format(D0,D1,D2))

    sleep(0.5)
