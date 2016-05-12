#!/usr/bin/env python
import getpass
import os
import sys
import webbrowser
import json

from simple_monitor_alert.sma import get_var_directory

REGISTER_NEW_PROJECT_URL = 'https://console.cloud.google.com/iam-admin/projects'

OAUTH_DEVICE_CODE_URL = 'https://accounts.google.com/o/oauth2/device/code'

var_directory = get_var_directory()
auth_file = os.path.join(var_directory, 'google-cloud-print.json')

if sys.version_info < (3, 0):
    input = raw_input


def register():
    print('You need to create access credentials to Google Cloud Print.')
    print('1. First, go to: {}'.format(REGISTER_NEW_PROJECT_URL))
    webbrowser.open(REGISTER_NEW_PROJECT_URL)
    print('2. Create a new project.')
    print('3. Go to "credentials" and create a new Oauth ID Client".')
    print('4. Select "other" in application type. You may need to create an authentication screen before.')
    print('5. Now you must have: client ID and client Secret.')
    print('Client ID example: 137998618127-d0p9bh4k48gugfh0l50u59okri7bd2xr.apps.googleusercontent.com')
    print('Client Secret example: 1kuJGYaCEWpGIcqTP7gNHd5c')
    client_id = input('Insert client ID: ')
    client_secret = getpass.getpass('Insert Client Secret (hidden): ')
    json.dump({'client_id': client_id, 'client_secret': client_secret}, open(auth_file, 'w'))
    print('Created {}'.format(auth_file))


if __name__ == '__main__':
    register()
