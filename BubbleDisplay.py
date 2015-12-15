#!/usr/bin/python
'''
Scroll message on a HP QDSP-6064 Bubble display using an
SN74HC595 Shift Register and 7 GPIO pins on a RaspberyPi

Or use a second shift register to control the cathodes for
the digits with -ds SR


GPIO pins are by BCM

First Shift register 74HC595N used to select segments

74HC595 Pin
    8           Connected to ground
    9           Serial Data Output to pin 14 of next shift register if used
    10          Master Reset (active LOW) so kept high +3V3
    11          Shift Register Clock input GPIO17 on Pi
    12          Storage Register Clock Input GPIO27 on Pi
    13          Output Enable (active LOW) so kept low with GND
    14          Serial Data Input GPIO22 on Pi
    16          +3V3

Output of shift register to bubble display pin number
[wiring info]

74HC595 Pin     74HC595 Output      QDSP-6064 Pin
    15              Q0                   2
    1               Q1                   3
    2               Q2                   7
    3               Q3                   8
    4               Q4                   9
    5               Q5                   11
    6               Q6                   12
    7               Q7                   5

GPIO to bubble display to select digit
G5                  1
G6                  10
G13                 4
G19                 6

Alternatively use another shift register

74HC595 Pin     74HC595 Output      QDSP-6064 Pin
    15              Q0                  1
    1               Q1                  10
    2               Q2                  4
    3               Q3                  6

Drive another bubble display with the rest of the outputs of the second
shift register

74HC595 Pin     74HC595 Output      QDSP-6064 Pin
    4               Q4                  1
    5               Q5                  10
    6               Q6                  4
    7               Q7                  6

GPIO to shift register
G17                 11 Shift Register Clock Input
G27                 12 Storage Register Clock Input
G22                 14 Serial Data Input

Output of shift register to segment of digit

74HC595 Pin          Segment                  QDSP-6064 Pin
    0           dot              DP              5
    1           top              A               12
    2           top right        B               11
    3           top left         F               9
    4           bottom           D               8
    5           middle           G               7
    6           bottom right     C               3
    7           bottom left      E               2
'''

import RPi.GPIO as GPIO
import time
import threading

class BubbleDisplay(object):
    'Operate an HP QDSP-6064 Bubble Display'

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

    def __init__(self,PIN_DATA=22,PIN_LATCH=27,PIN_CLOCK=17,**qwargs):
        '''
        PIN_DATA        -- GPIO pin number for data (default 22)
        PIN_LATCH       -- GPIO pin number for latch (default 27)
        PIN_CLOCK       -- GPIO pin number for clock (default 17)

        Qwargs:
        PIN_DIGITS      -- Array of pins used for selecting digits
                           (default [5,6,13,9]
        digits          -- How many characters 4 or 8 (default 4)
        digit_select    -- use GPIO or another Shift Register to select
                           digits (default 'G')
        '''
        self.message='playing with a retro bubble display on a raspberry pi 0123456789 ...'
        self.word='playing.'
        self.PIN_DATA=PIN_DATA
        self.PIN_LATCH=PIN_LATCH
        self.PIN_CLOCK=PIN_CLOCK
        if qwargs.has_key('PIN_DIGITS'):
            self.PIN_DIGITS=qwargs.get('PIN_DIGITS')
        else:
            self.PIN_DIGITS=[5,6,13,19]
        if qwargs.has_key('digits'):
            self.digits=qwargs.get('digits')
        else:
            self.digits=4
        if qwargs.has_key('digit_select'):
            self.digit_select=qwargs.get('digit_select')
        else:
            self.digit_select=4
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_DATA,GPIO.OUT)
        GPIO.setup(PIN_LATCH,GPIO.OUT)
        GPIO.setup(PIN_CLOCK,GPIO.OUT)

        if self.digit_select=='G':
            for i in PIN_DIGIT:
                GPIO.setup(i,GPIO.OUT,initial=GPIO.HIGH)

    def cleanup(self):
        print('BubbleDisplay Terminating')
        GPIO.cleanup()

    def set_segments(self,byte):
        #print(bin(byte))
        GPIO.output(self.PIN_LATCH, 0)
        for x in range(8):
            GPIO.output(self.PIN_DATA, (byte >> x) & 1)
            GPIO.output(self.PIN_CLOCK, 1)
            GPIO.output(self.PIN_CLOCK, 0)
        #GPIO.output(PIN_LATCH, 1)

    def set_digit(self,d):
        #if GPIO used for setting which digit (digit_select=='G')
        GPIO.output(self.PIN_DIGIT[d],0)

    def clear_digit(self):
        #if GPIO used for setting which digit (digit_select=='G')
        for i in self.PIN_DIGIT:
            GPIO.output(i,1)

    def show_string(self,s):
        for l in range(self.digits):
            if self.digit_select=='G':
                clear_digit()
                self.set_segments(self.font[s[l]])
                GPIO.output(self.PIN_LATCH,1)
                set_digit(l)
                time.sleep(0.0001)
            else:
                self.set_segments(~(128>>l) & 255)
                self.set_segments(self.font[s[l]])
                GPIO.output(self.PIN_LATCH,1)
                time.sleep(0.0001)
'''

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
'''
