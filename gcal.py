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

return flask.redirect(authorization_url)


state = flask.session['state']
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'],
    state=state)
flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

authorization_response = flask.request.url
flow.fetch_token(authorization_response=authorization_response)

credentials = flow.credentials
flask.session['credentials'] = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes}
