#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 background=dark

'''
0  dot              DP
1  top              A
2  top right        B
3  top left         F
4  bottom           D
5  middle           G
6  bottom right     C
7  bottom left      E
8
'''

font={
        'a':0b11101110,
        'b':0b11111000,
        'c':0b10011010,
        'd':0b11110100,
        'e':0b10111010,
        'f':0b10101010,
        'g':0b01111110,
        'h':0b11101100,
        'i':0b10001000,
        'j':0b11010100,
        'k':0b11101100,
        'l':0b10011000,
        'm':0b11000010,
        'n':0b11100000,
        'o':0b11011110,
        'p':0b10101110,
        'q':0b01101110,
        'r':0b10100000,
        's':0b01111010,
        't':0b10111000,
        'u':0b11011100,
        'v':0b11010000,
        'w':0b00011100,
        'x':0b11101100,
        'y':0b01111100,
        'z':0b10110110,
        '0':0b11011110,
        '1':0b01000100,
        '2':0b10110110,
        '3':0b01110110,
        '4':0b01101100,
        '5':0b01111010,
        '6':0b11111010,
        '7':0b01000110,
        '8':0b11111110,
        '9':0b01111110,
        '.':0b00000001,
        ' ':0b00000000,
        }
message='playing with a retro bubble display on a raspberry pi 0123456789 ...'
word='play'
import RPi.GPIO as GPIO,time,threading,atexit,signal
PIN_DATA=22
PIN_LATCH=27
PIN_CLOCK=17
PIN_DIGIT=[5,6,13,19]
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_DATA,GPIO.OUT)
GPIO.setup(PIN_LATCH,GPIO.OUT)
GPIO.setup(PIN_CLOCK,GPIO.OUT)

for i in PIN_DIGIT:
    GPIO.setup(i,GPIO.OUT,initial=GPIO.HIGH)

def cleanup( ):
    print('Terminating')
    GPIO.cleanup() 

atexit.register(cleanup)
signal.signal(signal.SIGTERM,cleanup)

def set_segments(byte):
    GPIO.output(PIN_LATCH, 0)
    for x in range(8):
        GPIO.output(PIN_DATA, (byte >> x) & 1)
        GPIO.output(PIN_CLOCK, 1)
        GPIO.output(PIN_CLOCK, 0)
    GPIO.output(PIN_LATCH, 1)

def set_digit(d):
    GPIO.output(PIN_DIGIT[d],0)

def clear_digit():
    for i in PIN_DIGIT:
        GPIO.output(i,1)
    
def show_string(s):
    for l in range(4):
        clear_digit()
        set_segments(font[s[l]])
        set_digit(l)
        time.sleep(0.0001)
        
class display_thread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            show_string(word)

myThread=display_thread()
myThread.start()
time.sleep(5)
try:
    while True:
        for x in range(len(message)):
            word=(message+'    ')[x:]
            time.sleep(0.2)
finally:
    cleanup()
