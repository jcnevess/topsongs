# coding: utf-8

import uuid
import os
import requests

from oauthlib.oauth2 import WebApplicationClient

CLIENT_ID = os.getenv('CLIENT_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

client = WebApplicationClient(CLIENT_ID)

header = {
    'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)
}

res = requests.get('https://api.genius.com/artists/16775/songs?sort=popularity&per_page=10',
    headers = header)

print(res.json())

transaction_id = uuid.uuid4()