# coding: utf-8

import requests

req = requests.get('https://api.genius.com/artists/16775/songs?sort=popularity&per_page=10')
print(req.json())