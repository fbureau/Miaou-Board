#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import glob
import requests
import buttonshim
import time
import yaml
import fontawesome as fa
from font_fredoka_one import FredokaOne
from font_source_sans_pro import SourceSansPro
from font_source_serif_pro import SourceSerifPro
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from inky import InkyPHAT
from inky.auto import auto
from common import text_wrap
import datetime
import sys
import pickle
import os.path
import locale
from re import search
from oauth2client import client
from googleapiclient import sample_tools


print(fa.icons['thumbs-up'])
print(fa["font-awesome"], "FontAwesome is Awesome", fa["fort-awesome"])

def main(argv):
    with open("config/config.yaml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    # Get the current path
    PATH = os.path.dirname(__file__)

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

    kitty_icon = "agenda"

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
    fontawsome = ImageFont.truetype(fa, 12)

    current_date = time.strftime("%d/%m %H:%M")
    
    draw.rectangle([(160, 0), (212, 15)], fill=inky_display.WHITE, outline=None)
    draw.text((165, 3), current_date, inky_display.BLACK, font=font_sm)

    draw.text((12, 11), "Agenda", inky_display.WHITE, font=font_lg)
    draw.line((12,34, 135,34),2)

    now = datetime.datetime.today().isoformat() + 'Z'
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).isoformat() + 'Z'
    
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar.readonly')

    try:
        page_token = None
        while True:
            events_result = service.events().list(calendarId='primary', timeMin=yesterday, timeMax=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])
            y = 36
            if not events:
                draw.text((12, 36), "Rien aujourd'hui !", inky_display.WHITE, font=font)
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = datetime.datetime.strptime(start, '%Y-%m-%d')

                if str(start) != str((datetime.datetime.today() - datetime.timedelta(1)).strftime('%Y-%m-%d 00:00:00')):
                    if search('Poubelle', event['summary']):
                        the_event = event['summary']
                        the_icon = fa.icons['fa-trash']
                    elif search('Encombrants', event['summary']):
                        the_event = "Encombrants demain"
                    elif search('Anniversaire', event['summary']):
                        the_event = "Aniversaire " + event['summary'].replace('Anniversaire ', '')
                    else:
                        the_event = start.strftime('%A %d/%m') + " : " + event['summary']
                    
                    draw.text((12, y), the_icon, inky_display.WHITE, font=fontawsome)
                    draw.text((22, y), the_event, inky_display.WHITE, font=font)
            if not page_token:
                break

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run'
              'the application to re-authorize.')
        
    inky_display.set_image(img)
    inky_display.show()
    print ("Display updated")

if __name__ == '__main__':
    main(sys.argv)
