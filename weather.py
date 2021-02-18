#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import lnetatmo
from meteocalc import Temp, feels_like
import requests
import json
from geopy.geocoders import Nominatim
from PIL import Image, ImageFont
import inkyphat
import buttonshim
import time

with open("config/config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

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


#display datas 
temp = 'Température extérieur : ' +str(t_ext) + '°C'
print(temp)
print('Tx humidité : ' + str(h_ext) + '%')
print('Ressentie : ' + str(round(fl.c,1)) + '°C')
print('Vitesse du vent : ' + str(round(ow_wind_speed,1)) + 'm/s')

#Inkyfat
inkyphat = InkyPHAT('red')

font = ImageFont.truetype(inkyphat.fonts.FredokaOne, 22)
inkyphat.set_image("resources/backdrop.png")
datetime = time.strftime("%d/%m %H:%M")

inkyphat.text((36, 12), datetime, inkyphat.WHITE, font=font)
inkyphat.text((36, 12), temp, inkyphat.WHITE, font=font)

inkyphat.show()
