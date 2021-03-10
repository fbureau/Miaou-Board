#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime 
import pickle
import os.path
import locale
from re import search
import google.oauth2.credentials
import google_auth_oauthlib.flow


flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/calendar.readonly'])

flow.redirect_uri = 'http://192.168.1.18/oauth2callback'
 
authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')
 
 
 
