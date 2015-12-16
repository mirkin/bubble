#!/usr/bin/python
'''
scroll a message on a retro bubble display
'''

import argparse
import BubbleDisplay as retro
import atexit
import signal
import time

message='playing with a retro bubble display on a raspberry pi 0123456789 ...'
parser=argparse.ArgumentParser(description='Bubble Display Scroller')
parser.add_argument("-ds",help="Digit Select GPIO [G] or Shift Register [SR]",
                    choices=["G","SR"],default="G")
parser.add_argument("--message","-m",help="Message to scroll",default=message)
parser.add_argument("--digits","-d",help="How many digits 4 or 8",default=4,
                    choices=[4,8],type=int)
parser.add_argument("--firstMessage","-fm",help="message displayed before scrolling"
                    ,default="0bubble0")
args=parser.parse_args()
message=args.message.center(len(args.message)+2*(1+args.digits),' ')
word=args.firstMessage
my_bubble=retro.BubbleDisplay(22,27,17,digit_select=args.ds,digits=args.digits)


def cleanup( ):
    print('scroll_bubble Terminating')
    my_bubble.cleanup()

atexit.register(cleanup)
signal.signal(signal.SIGTERM,cleanup)
my_bubble.show_static_message(word)
time.sleep(3)
my_bubble.show_scroll_message(message)
