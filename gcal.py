#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime 
import pickle
import os.path
import locale
from re import search
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
 
def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

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


if __name__ == '__main__':
    main()
