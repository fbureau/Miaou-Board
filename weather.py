#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import yaml
import sys
import os
import lnetatmo
from meteocalc import Temp, feels_like
import requests
import json
from geopy.geocoders import Nominatim
from font_fredoka_one import FredokaOne
from font_amatic_sc import AmaticSC
from font_caladea import Caladea
from font_hanken_grotesk import HankenGrotesk
from font_intuitive import Intuitive
from font_roboto import Roboto
from font_source_sans_pro import SourceSansPro
from font_source_serif_pro import SourceSerifPro
from PIL import Image, ImageFont, ImageDraw
import buttonshim
import time
from inky import InkyPHAT
from inky.auto import auto

with open("config/config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Get the current path
PATH = os.path.dirname(__file__)

# Get geoloc
geolocator = Nominatim(user_agent="pi_dash")
location = geolocator.geocode(cfg["openweather"]["adresse"])

# Get Wind speed from Openweather
base_url = "http://api.openweathermap.org/data/2.5/weather?"
complete_url = base_url + "appid=" + cfg["openweather"]["api_key"] + "&units=metricweather&lat="+ str(location.latitude) +"&lon="+ str(location.longitude)
response = requests.get(complete_url)
x = response.json()
ow_wind_speed = x["wind"]["speed"]
ow_feels_like = x["main"]["feels_like"]


# Get data from the station
authorization = lnetatmo.ClientAuth(
    clientId = cfg["netatmo"]["clientId"],
    clientSecret = cfg["netatmo"]["clientSecret"],
    username = cfg["netatmo"]["username"],
    password = cfg["netatmo"]["password"]
)

weatherData = lnetatmo.WeatherStationData(authorization)

t_ext = weatherData.lastData()['Exterieur']['Temperature']
h_ext = weatherData.lastData()['Exterieur']['Humidity']


# Compute Feels like temperature
fl = feels_like(Temp(t_ext, unit='c'), humidity=h_ext, wind_speed=ow_wind_speed)


# Display datas
print('Temperature : ' + str(t_ext) + '°C')
print('Tx humidité : ' + str(h_ext) + '%')
print('Ressentie : ' + str(round(fl.c,1)) + '°C')
print('Vitesse du vent : ' + str(round(ow_wind_speed,1)) + 'm/s')

# Inkyphat conf

try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

inky_display.set_border(inky_display.WHITE)

# Create the palette
pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

# Inkyphat functions

def create_mask(source, mask=(inky_display.BLACK, inky_display.WHITE, inky_display.RED)):
    """Create a transparency mask.
    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.
    :param mask: Optional list of Inky pHAT colours to allow.
    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image

# Display on Inkyphat

img = Image.open(os.path.join(PATH, "resources/backdrop_miaou.png")).resize(inky_display.resolution)
img = img.convert("RGB").quantize(palette=pal_img)
draw = ImageDraw.Draw(img)

icons = {}
masks = {}

kitty_icon = "pirate"

# Load our icon files and generate masks
for icon in glob.glob("resources/icons/kitty-*.png"):
    icon_name = icon.split("kitty-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icon_image = icon_image.convert("RGB").quantize(palette=pal_img)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

# Process the image using the palette

img.paste(icons[kitty_icon], (154, 49), masks[kitty_icon])

font = ImageFont.truetype(Caladea, 12)
font_sm = ImageFont.truetype(FredokaOne, 8)
font_lg = ImageFont.truetype(HankenGrotesk, 18)

datetime = time.strftime("%d/%m %H:%M")

draw.text((162, 11), datetime, inky_display.BLACK, font=font_sm)

draw.text((12, 11), "Météo", inky_display.WHITE, font=font_lg)
draw.line((12,34, 140,34),2)
draw.text((12, 36), "Temperature:", inky_display.WHITE, font=font)
draw.text((94, 36), u"{:.1f}°C".format(t_ext,1), inky_display.WHITE, font=font)
draw.text((12, 48), "Ressentie:", inky_display.WHITE, font=font)
draw.text((78, 48), u"{:.1f}°C".format(fl.c,1), inky_display.WHITE, font=font)
draw.text((12, 60), "Humidite:", inky_display.WHITE, font=font)
draw.text((78, 60), u"{:.1f}%".format(h_ext,0), inky_display.WHITE, font=font)

inky_display.set_image(img)
inky_display.show()
print ("Display updated")

sys.exit()
