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
from PIL import Image, ImageFont, ImageDraw
import buttonshim
import time
import inkyphat
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


# Inkyfat functions

def create_mask(source, mask=(inkyphat.WHITE, inkyphat.BLACK, inkyphat.RED)):
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

# Display on Inkyfat

try:
    inkyphat = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

if inkyphat.resolution not in ((212, 104), (250, 122)):
    w, h = inkyphat.resolution
    raise RuntimeError("This example does not support {}x{}".format(w, h))

inkyphat.set_border(inkyphat.BLACK)

# img = Image.open(os.path.join(PATH, "resources/backdrop_miaou.png")).resize(inkyphat.resolution)
img = Image.open("resources/backdrop_miaou.png")
draw = ImageDraw.Draw(img)

icons = {}
masks = {}

kitty_icon = "flower"

# Load our icon files and generate masks
for icon in glob.glob("resources/icons/kitty-*.png"):
    icon_name = icon.split("kitty-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

font = ImageFont.truetype(FredokaOne, 10)
font_sm = ImageFont.truetype(FredokaOne, 6)
font_lg = ImageFont.truetype(FredokaOne, 18)

datetime = time.strftime("%d/%m %H:%M")

draw.text((154, 10), datetime, inkyphat.WHITE, font=font_sm)

draw.text((36, 34), "Temperature:", inkyphat.WHITE, font=font)
draw.text((110, 34), u"{:.1f}°C".format(t_ext,1), inkyphat.WHITE, font=font)
draw.text((36, 46), "Ressentie:", inkyphat.WHITE, font=font)
draw.text((100, 46), u"{:.1f}°C".format(fl.c,1), inkyphat.WHITE, font=font)
draw.text((36, 58), "Humidite:", inkyphat.WHITE, font=font)
draw.text((100, 58), u"{:.1f}%".format(h_ext,0), inkyphat.WHITE, font=font)

# Create the palette
pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

# Process the image using the palette
img = Image.convert("RGB").quantize(palette=pal_img)

img.paste(icons[kitty_icon], (154, 49), masks[kitty_icon])

inkyphat.set_image(img)
inkyphat.show()
print ("Display updated")

sys.exit()
