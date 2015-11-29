#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 background=dark

'''
Scroll message on a HP QDSP-6064 Bubble display using an
SN74HC595 Shift Register and 7 GPIO pins on a RaspberyPi

Or use a second shift register to control the cathodes for
the digits with -ds SR


GPIO pins are by BCM

Shift register 74HC595N Other Pins
8                   Connected to ground
9                   Serial Data Output not used
10                  Master Reset (active LOW) so kept high +3V3
13                  Output Enable (active LOW) so kept low with GND
16                  +3V3

Output of shift register to bubble display pin number
[wiring info]

Q0                   2
Q1                   3
Q2                   7
Q3                   8
Q4                   9
Q5                   11
Q6                   12
Q7                   5

GPIO to bubble display to select digit
G5                  1
G6                  10
G13                 4
G19                 6

GPIO to shift register
G17                 11 Shift Register Clock Input
G27                 12 Storage Register Clock Input
G22                 14 Serial Data Input

Output of shift register to segment of digit
0  dot              DP
1  top              A
2  top right        B
3  top left         F
4  bottom           D
5  middle           G
6  bottom right     C
7  bottom left      E
'''

import RPi.GPIO as GPIO
import time
import threading
import atexit
import signal
import argparse

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
word='playing.'
PIN_DATA=22
PIN_LATCH=27
PIN_CLOCK=17
PIN_DIGIT=[5,6,13,19]
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_DATA,GPIO.OUT)
GPIO.setup(PIN_LATCH,GPIO.OUT)
GPIO.setup(PIN_CLOCK,GPIO.OUT)

parser=argparse.ArgumentParser(description='Bubble Display Scroller')
parser.add_argument("-ds",help="Digit Select GPIO [G] or Shift Register [SR]",
                    choices=["G","SR"],default="G")
parser.add_argument("--message","-m",help="Message to scroll",default=message)
parser.add_argument("--digits","-d",help="How many digits 4 or 8",default=4,
                    choices=[4,8],type=int)
parser.add_argument("--firstMessage","-fm",help="message displayed before scrolling"
                    ,default="0bubble0")
args=parser.parse_args()
#message=('{:^'+str(args.digits)+'}').format(args.message)
#print'{:^'+str(args.digits)+'}'
#print ('{:^'+str(args.digits)+'}').format(args.message)
message=args.message.center(len(args.message)+2*(1+args.digits),' ')
word=args.firstMessage
print(args.ds)
for i in PIN_DIGIT:
    GPIO.setup(i,GPIO.OUT,initial=GPIO.HIGH)

def cleanup( ):
    print('Terminating')
    GPIO.cleanup()

atexit.register(cleanup)
signal.signal(signal.SIGTERM,cleanup)

def set_segments(byte):
    #print(bin(byte))
    GPIO.output(PIN_LATCH, 0)
    for x in range(8):
        GPIO.output(PIN_DATA, (byte >> x) & 1)
        GPIO.output(PIN_CLOCK, 1)
        GPIO.output(PIN_CLOCK, 0)
    #GPIO.output(PIN_LATCH, 1)

def set_digit(d):
    GPIO.output(PIN_DIGIT[d],0)

def clear_digit():
    for i in PIN_DIGIT:
        GPIO.output(i,1)

def show_string(s):
    for l in range(args.digits):
        if args.ds=='G':
            clear_digit()
            set_segments(font[s[l]])
            GPIO.output(PIN_LATCH,1)
            set_digit(l)
            time.sleep(0.0001)
        else:
            set_segments(~(128>>l) & 255)
            set_segments(font[s[l]])
            GPIO.output(PIN_LATCH,1)
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
        for x in range(len(message)-args.digits):
            word=message[x:]
            time.sleep(0.2)
finally:
    cleanup()
