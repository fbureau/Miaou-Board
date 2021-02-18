#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import signal
import buttonshim
import inkyphat
import os
import sys
from PIL import Image, ImageFont
import inkyphat
import time
from urllib.request import urlopen
import textwrap


sys.tracebacklimit = None

def flash_led(interval, times, r, g, b):
    for i in range(times):
        buttonshim.set_pixel(r, g, b)
        time.sleep(interval)
        buttonshim.set_pixel(0, 0, 0)
        time.sleep(interval)

def buttonflash():
    flash_led(0.025, 3, 255, 255, 255)

def runprocess(file):
    try:
        # run process
        process = subprocess.Popen(file, shell=True)
        # flash green led to show its working
        flash_led(0.5, 14, 0, 255, 0)
        # wait for the process to complete
        process.communicate()
        # flash blue led to show its finshed
        flash_led(0.05, 5, 0, 0, 255)   
    except Exception as error:
        printtoscreen("Error", error)

def printtoscreen(title="", content="Error"):
    
    # draw a rectangle of white to clear previous screen if using a loop - as in twitter output
    inkyphat.rectangle([(0, 0), (212, 104)], fill=inkyphat.WHITE, outline=None)

    if len(content) < 200:
        fontsize = 10
        charwidth = 29
        lineheight = 9
    else:
        fontsize = 6
        charwidth = 41
        lineheight = 6

    font = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", fontsize)
    fontmedium = ImageFont.truetype("/home/pi/Pimoroni/inkyphat/fonts/elec.ttf", 10)
    inkyphat.set_rotation(180)
    inkyphat.set_border(inkyphat.BLACK)

    # title
    inkyphat.rectangle([(1, 1), (210, 13)], fill=inkyphat.BLACK, outline=None)
    inkyphat.text((2, 3), title, inkyphat.WHITE, font=fontmedium)

    # main body of text - line wrapped 
    y = 17
    for line in textwrap.wrap(content, charwidth):
         inkyphat.text((2, y), line, inkyphat.BLACK, font=font)
         y = y + lineheight

    flash_led(0.5, 3, 0, 255, 0)

    inkyphat.show()

    flash_led(0.05, 5, 0, 0, 255)

def wait_for_internet_connection():
    while True:
        try:
            response = urlopen('http://www.google.com',timeout=1).read()
            runprocess("/home/pi/git/Miaou-Board/weather.py")
            return
        except urlopen.URLError:
            pass
            printtoscreen("Message","Waitng for internet connection")


# Run initial python script weather.py when internet connection established
wait_for_internet_connection()

signal.pause()
