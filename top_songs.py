# coding: utf-8

import json
import uuid
import os
import requests
import boto3

from oauthlib.oauth2 import WebApplicationClient
from flask import Flask

CLIENT_ID = os.getenv('CLIENT_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ENDPOINT_URL = os.getenv('ENDPOINT_URL')

def create_songs_table(dynamodb = None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb', endpoint_url=ENDPOINT_URL)

        table = dynamodb.create_table(
            TableName='PopularSongs',
            KeySchema=[
                {
                    'AttributeName': 'TransactionID',
                    'KeyType': 'HASH' # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'TransactionID',
                    'AttributeType': 'S'
                },
                                {
                    'AttributeName': 'ArtistID',
                    'AttributeType': 'S'
                },
                                {
                    'AttributeName': 'ArtistName',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'ArtistSongs',
                    'AttributeType': 'L'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )    

        return table


def put_songs(transaction_id, artist_id, artist_name, artist_songs, dynamodb = None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb', endpoint_url=ENDPOINT_URL)
 
    table = dynamodb.Table('PopularSongs')
    response = table.put_item(
        Item={
            'TransactionID': transaction_id,
            'ArtistID': artist_id,
            'ArtistName': artist_name,
            'ArtistSongs': artist_songs
        }
    )
    return response


# TODO: Do/call all authentication here
# SIA: 16775
def prepare_response(artist_id):
    client = WebApplicationClient(CLIENT_ID)

    header = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    res = requests.get(f'https://api.genius.com/artists/{artist_id}',
        headers = header)

    artist_name = res.json()['response']['artist']['name']

    res = requests.get(f'https://api.genius.com/artists/{artist_id}/songs?sort=popularity&per_page=10',
        headers = header)

    # Fixes ill formated data
    res_data = res.text.replace('\xa0', ' ')

    res_data = json.loads(res_data)
    artist_songs = res_data['response']['songs']

    transaction_id = str(uuid.uuid4())

    response = {
        "transaction_id": transaction_id,
        "artist_id": artist_id,
        "artist_name": artist_name,
        "artist_songs": artist_songs
    }

    return response


app = Flask(__name__)

#dynamodb = boto3.resource(
#    'dynamodb',
#    endpoint_url=ENDPOINT_URL)

# TODO: Check if it exists before creation
# create_songs_table(dynamodb)

@app.get('/')
def index():
    return 'Welcome to the Top Songs API. Try using /topsongs/:id'

@app.get('/topsongs/<song_id>')
def top_songs(song_id):
    return json.dumps(prepare_response(song_id))
    