#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import yaml
import sys
import os
import lnetatmo
from meteofrance_api import MeteoFranceClient
from meteofrance_api.model import Place
from datetime import datetime
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
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import buttonshim
import time
from inky import InkyPHAT
from inky.auto import auto

with open("config/config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)


## OpenWeather :    
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

ow_w = x["weather"]
for ow_w_d in ow_w:
    ow_w_d_icon = ow_w_d["icon"]

ow_wind_speed = x["wind"]["speed"]
ow_feels_like = x["main"]["feels_like"]


## Meteo France :
client = MeteoFranceClient()

list_places = client.search_places(cfg["openweather"]["city"])
my_place = list_places[0]

my_place_weather_forecast = client.get_forecast_for_place(my_place)
my_place_daily_forecast = my_place_weather_forecast.current_forecast

mf_wind_speed = my_place_daily_forecast["wind"]["speed"]
mf_description = my_place_daily_forecast["weather"]["desc"]
mf_icon = my_place_daily_forecast["weather"]["icon"]


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
fl = feels_like(Temp(t_ext, unit='c'), humidity=h_ext, wind_speed=mf_wind_speed)


# Display datas
print('Temperature : ' + str(t_ext) + '°C')
print('Tx humidité : ' + str(h_ext) + '%')
print('Ressentie : ' + str(round(fl.c,1)) + '°C')
print('Vitesse du vent : ' + str(round(mf_wind_speed,1)) + 'm/s')

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

icon_map = {
    "snow": ["p17j","p17n","p18j","p18n","p21j","p21n","p22j","p22n","p23j","p23n"],
    "rain": ["p9j","p9n","p10j","p10n","p11j","p11n","p12j","p12n","p13j","p13n","p14j","p14n","p15j","p15n","p19j","p19n","p20j","p20n"],
    "cloud": ["p2j", "p2n","p3j","p3n","p4j","p4n","p5j","p5n","p6j","p6n","p7j","p7n","p8j","p8n"],
    "sun": ["p1j","p1n"],
    "storm": ["p16j","p16n","p24j","p24n","p25j","p25n","p26j","p26n","p27j","p27n","p28j","p28n","p29j","p29n","p30j","p30n"],
    "fog": ["p31j","p31n","p32j","p32n","p33j","p33n","p34j","p34n"]
}

try:
    if t_ext >= 28:
        kitty_icon = "hot"
    elif t_ext <= 5 and ow_icon != "snow":
        kitty_icon = "froid"
    elif t_ext <= 5 and ow_icon == "snow":
        kitty_icon = "snow"
    elif t_ext <= 5 and ow_icon == "rain":
        kitty_icon = "rain"
    else:
        for ow_icon in icon_map:
            if mf_icon in icon_map[ow_icon]:
                kitty_icon = ow_icon
                break
except:
    kitty_icon = "erreur"

print('Icone : ' + kitty_icon)

# Load our icon files and generate masks
for icon in glob.glob("resources/icons/kitty-*.png"):
    icon_name = icon.split("kitty-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icon_image = icon_image.convert("RGB").quantize(palette=pal_img)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

# Process the image using the palette

img.paste(icons[kitty_icon], (137, 22), masks[kitty_icon])

font = ImageFont.truetype(SourceSansPro, 12)
font_sm = ImageFont.truetype(SourceSansPro, 8)
font_lg = ImageFont.truetype(FredokaOne, 18)

datetime = time.strftime("%d/%m %H:%M")

draw.rectangle([(160, 0), (212, 15)], fill=inky_display.WHITE, outline=None)
draw.text((165, 3), datetime, inky_display.BLACK, font=font_sm)

draw.text((12, 11), "Météo", inky_display.WHITE, font=font_lg)
draw.line((12,34, 135,34),2)
draw.text((12, 36), "Temperature:", inky_display.WHITE, font=font)
draw.text((89, 36), u"{:.1f}°C".format(t_ext,1), inky_display.WHITE, font=font)
draw.text((12, 48), "Ressentie:", inky_display.WHITE, font=font)
draw.text((70, 48), u"{:.1f}°C".format(fl.c,1), inky_display.WHITE, font=font)
draw.text((12, 60), "Humidite:", inky_display.WHITE, font=font)
draw.text((70, 60), u"{:.1f}%".format(h_ext,0), inky_display.WHITE, font=font)
draw.text((12, 72), "Description:", inky_display.WHITE, font=font)
draw.text((70, 72), mf_description, inky_display.WHITE, font=font)

inky_display.set_image(img)
inky_display.show()
print ("Display updated")
