#!/usr/bin/env python
import getpass
import os
import sys
import webbrowser
import json
from json.decoder import JSONDecodeError

import requests
import time

from simple_monitor_alert.sma import get_var_directory

GRANT_TYPE = 'http://oauth.net/grant_type/device/1.0'
GRANT_TYPE_REFRESH = 'refresh_token'
SCOPE = 'https://www.googleapis.com/auth/cloudprint'
REGISTER_NEW_PROJECT_URL = 'https://console.developers.google.com/iam-admin/projects'
OAUTH_DEVICE_CODE_URL = 'https://accounts.google.com/o/oauth2/device/code'
OAUTH_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
SEARCH_PRINTS = 'https://www.google.com/cloudprint/search'

var_directory = get_var_directory()
auth_file = os.path.join(var_directory, 'google-cloud-print.json')

if sys.version_info < (3, 0):
    input = raw_input


class Auth(requests.auth.AuthBase):
    def __init__(self, file=None):
        self.file = file or auth_file
        if not self.file:
            print('You need execute "register". Look at the instructions.')
            raise SystemExit
        self.data = json.load(open(self.file))

    def renew(self):
        r = requests.post(OAUTH_TOKEN_URL, {'client_secret': self.data['client_secret'],
                                            'client_id': self.data['client_id'], 'grant_type': GRANT_TYPE_REFRESH,
                                            'refresh_token': self.data['refresh_token']})
        self.data.update(r.json())
        self.save()

    def save(self):
        json.dump(self.data, open(self.file, 'w'))

    def __call__(self, r):
        r.headers['Authorization'] = '{token_type} {access_token}'.format(**self.data)
        return r


def register():
    print('You need to create access credentials to Google Cloud Print.')
    print('1. First, go to: {}'.format(REGISTER_NEW_PROJECT_URL))
    webbrowser.open(REGISTER_NEW_PROJECT_URL)
    print('2. Create a new project.')
    print('3. Go to "credentials" and create a new Oauth ID Client".')
    print('Credentials url: https://console.developers.google.com/apis/credentials')
    print('4. Select "other" in application type. You may need to create an authentication screen before.')
    print('5. Now you must have: client ID and client Secret.')
    print('Client ID example: 137998618127-d0p9bh4k48gugfh0l50u59okri7bd2xr.apps.googleusercontent.com')
    print('Client Secret example: 1kuJGYaCEWpGIcqTP7gNHd5c')
    time.sleep(2)
    client_id = input('Insert client ID: ')
    client_secret = getpass.getpass('Insert Client Secret (hidden): ')
    data = {}
    while True:
        r = requests.post(OAUTH_DEVICE_CODE_URL, {'scope': SCOPE, 'client_id': client_id})
        data = r.json()
        print('Go to {verification_url} and insert: {user_code}'.format(**data))
        print('INSERT CODE ==========> {} <========== INSERT CODE'.format(data['user_code']))
        webbrowser.open(data['verification_url'])
        time.sleep(2)
        print("[!!] Press enter when ready")
        input('[Press enter]')
        r = requests.post(OAUTH_TOKEN_URL, {'client_secret': client_secret, 'code': data['device_code'],
                                            'client_id': client_id, 'grant_type': GRANT_TYPE})
        data = r.json()
        if data.get('error'):
            print('Error: {error}'.format(**data))
            print('Sorry, It will start again.')
        else:
            print('Great!')
            break
    data.update({'client_id': client_id, 'client_secret': client_secret})
    json.dump(data, open(auth_file, 'w'))
    print('Created {}'.format(auth_file))


def get_prints(auth=None):
    auth = auth or Auth()
    r = None
    for i in range(2):
        r = requests.get(SEARCH_PRINTS, auth=auth)
        if r.status_code == 403 and i == 1:
            raise SystemExit('Renew token failed.')
        elif r.status_code == 403:
            auth.renew()
        else:
            break
    data = r.json()
    for printer in data['printers']:
        if printer['name'] in ['Save to Google Docs']:
            continue
        print('printer_status({id}).name = "{displayName}"'.format(**printer))
        print('printer_status({id}).expected = "ONLINE"'.format(**printer))
        print('printer_status({id}).value = "{connectionStatus}"'.format(**printer))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'register':
        register()
    else:
        get_prints()
