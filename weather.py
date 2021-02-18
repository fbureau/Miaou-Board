#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import glob
import yaml
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
temp = 'Température : ' +str(t_ext) + '°C'
print(temp)
print('Tx humidité : ' + str(h_ext) + '%')
print('Ressentie : ' + str(round(fl.c,1)) + '°C')
print('Vitesse du vent : ' + str(round(ow_wind_speed,1)) + 'm/s')

# Display on Inkyfat
try:
    inkyphat = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

if inkyphat.resolution not in ((212, 104), (250, 122)):
    w, h = inkyphat.resolution
    raise RuntimeError("This example does not support {}x{}".format(w, h))

inkyphat.set_border(inkyphat.BLACK)

img = Image.open(os.path.join(PATH, "resources/backdrop.png")).resize(inkyphat.resolution)
draw = ImageDraw.Draw(img)
    
font = ImageFont.truetype(FredokaOne, 22)

datetime = time.strftime("%d/%m %H:%M")

draw.text((36, 12), datetime, inkyphat.WHITE, font=font)
draw.text((36, 34), temp, inkyphat.WHITE, font=None)


inkyphat.set_image(img)
inkyphat.show()
