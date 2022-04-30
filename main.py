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

artist_id = 16775

res = requests.get(f'https://api.genius.com/artists/{artist_id}',
    headers = header)

artist_name = res.json()['response']['artist']['name']

res = requests.get(f'https://api.genius.com/artists/{artist_id}/songs?sort=popularity&per_page=10',
    headers = header)

print(res.json()['response'])

transaction_id = uuid.uuid4()