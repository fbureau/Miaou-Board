#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sys
import pickle
import os.path
import locale
from re import search
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import sample_tools
from oauth2client import client

def main(argv):
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar.readonly')

    try:
        page_token = None
        while True:
            # Call the Calendar API
            now = datetime.datetime.today().isoformat() + 'Z'
            yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).isoformat() + 'Z'   

            events_result = service.events().list(calendarId='primary', timeMin=yesterday, timeMax=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print(' ')
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                if str(start) != str((datetime.datetime.today() - datetime.timedelta(1)).strftime('%Y-%m-%d 00:00:00')):
                    if search('Poubelle', event['summary']):
                        print("Il faut sortir la " + str.lower(event['summary']))
                    elif search('Encombrants', event['summary']):
                        print("Les encombrants doivent passer demain")
                    elif search('Anniversaire', event['summary']):
                        print("C'est l'aniversaire de " + event['summary'].replace('Anniversaire ', '') )
                    else:
                        print(start.strftime('%A %d/%m') + " : " + event['summary'])

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run'
              'the application to re-authorize.')

if __name__ == '__main__':
    main(sys.argv)
