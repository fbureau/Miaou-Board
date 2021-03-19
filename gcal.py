#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sys
import pickle
import os.path
import locale
from re import search
from oauth2client import client
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account

try:
    scope = "https://www.googleapis.com/auth/calendar.readonly"
    creds = None
    
    if os.path.exists('client_secrets.json'):
      creds = service_account.Credentials.from_service_account_file('client_secrets.json')
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    
    while True:
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
                break

except client.AccessTokenRefreshError:
    print('The credentials have been revoked or expired, please re-run'
          'the application to re-authorize.')
