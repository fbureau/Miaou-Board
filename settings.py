#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import subprocess
import buttonshim
import time
from datetime import datetime
from font_fredoka_one import FredokaOne
from font_source_sans_pro import SourceSansPro
from font_source_serif_pro import SourceSerifPro
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from inky import InkyPHAT
from inky.auto import auto
import common

# Get the current path
PATH = os.path.dirname(__file__)

#  Get address IP
ip_adress = subprocess.getoutput('hostname -i')

# Get Wifi name
networks = subprocess.getoutput('iwgetid -r')

# Inkyphat conf
try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

inky_display.set_border(inky_display.WHITE)

# Create the palette
pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

# Display on Inkyphat
img = Image.open(os.path.join(PATH, "resources/backdrop_miaou.png")).resize(inky_display.resolution)
img = img.convert("RGB").quantize(palette=pal_img)
draw = ImageDraw.Draw(img)

icons = {}
masks = {}

kitty_icon = "technique"

# Load our icon files and generate masks
for icon in glob.glob("resources/icons/kitty-*.png"):
    icon_name = icon.split("kitty-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icon_image = icon_image.convert("RGB").quantize(palette=pal_img)
    icons[icon_name] = icon_image

# Process the image using the palette
img.paste(icons[kitty_icon], (140, 22))

font = ImageFont.truetype(SourceSerifPro, 12)
font_sm = ImageFont.truetype(SourceSerifPro, 8)
font_lg = ImageFont.truetype(FredokaOne, 18)

datetime = time.strftime("%d/%m %H:%M")

draw.rectangle([(160, 0), (212, 15)], fill=inky_display.WHITE, outline=None)
draw.text((165, 3), datetime, inky_display.BLACK, font=font_sm)

draw.text((12, 11), "Configuration", inky_display.WHITE, font=font_lg)
draw.line((12,34, 135,34),2)
draw.text((12, 36), "Adresse IP:", inky_display.WHITE, font=font)
draw.text((76, 36), ip_adress, inky_display.WHITE, font=font)
draw.text((12, 48), "Wifi:", inky_display.WHITE, font=font)
draw.text((45, 48), networks, inky_display.WHITE, font=font)

inky_display.set_image(img)
inky_display.show()
print ("Display updated")
