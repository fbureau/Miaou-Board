#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import requests
import buttonshim
import time
import yaml
from datetime import datetime
from font_fredoka_one import FredokaOne
from font_source_sans_pro import SourceSansPro
from font_source_serif_pro import SourceSerifPro
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from inky import InkyPHAT
from inky.auto import auto
from common import text_wrap

with open("config/config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Get the current path
PATH = os.path.dirname(__file__)

# Get RATP infos
url_ratp = "https://api-ratp.pierre-grimaud.fr/v4/traffic/" + cfg["ratp"]["type"] + "/" + cfg["ratp"]["line"]
info_ratp = requests.get(url_ratp) 
ratp = info_ratp.json() 
trafic = ratp.get('result', [])

ratp_msg = "RER " + ratp["result"]["line"] + " : " + ratp["result"]["message"]
print(ratp_msg)

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

kitty_icon = "ratp"

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

draw.text((12, 11), "Trafic RATP", inky_display.WHITE, font=font_lg)
draw.line((12,34, 135,34),2)

text = "This could be a single line text but its too long to fit in one."
lines = text_wrap(ratp_msg, font_sm, 130)
line_height = 12

y = 36
for line in lines:
    draw.text((12, y), line, inky_display.WHITE, font=font_sm)
    y = y + line_height

inky_display.set_image(img)
inky_display.show()
print ("Display updated")
