# coding: utf-8

import json
import uuid
import requests
import boto3
import redis

from os import getenv
from distutils.util import strtobool
from botocore.exceptions import ClientError
from flask import Flask, request

ACCESS_TOKEN = getenv('ACCESS_TOKEN')
DYNAMO_ENDPOINT = getenv('DYNAMO_ENDPOINT')
REDIS_PORT = getenv('REDIS_PORT')

# SIA: 16775

def create_songs_table(dynamodb = None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb', endpoint_url=DYNAMO_ENDPOINT)

    try:
        table = dynamodb.create_table(
            TableName='popular_songs',
            KeySchema=[
                {
                    'AttributeName': 'artist_id',
                    'KeyType': 'HASH' # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'transaction_id',
                    'AttributeType': 'S'
                },
                                {
                    'AttributeName': 'artist_id',
                    'AttributeType': 'S'
                },
                                {
                    'AttributeName': 'artist_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'artist_songs',
                    'AttributeType': 'B'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            },
            BillingMode="PAY_PER_REQUEST"
        )

    except ClientError as err:
        # Table already exists
        if err.response["Error"]["Code"] == 'ResourceInUseException':
            pass
        else:
            raise err

    return table


def persist_songs(transaction_id, artist_id, artist_name, artist_songs, dynamodb = None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb', endpoint_url=DYNAMO_ENDPOINT)

    table = dynamodb.Table('popular_songs')
    response = table.put_item(
        Item={
            'transaction_id': transaction_id,
            'artist_id': artist_id,
            'artist_name': artist_name,
            'artist_songs': artist_songs
        }
    )
    return response


def retrieve_external_response(artist_id):
    header = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    # The only way to get artist names accurately is making this call
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


# Cache expires in 7 days (604800 secs)
def cache_songs(redis_db, response, expiration = 604800):
    redis_db.setex('top_songs_' + response['artist_id'], expiration, json.dumps(response))


################# MAIN APP ##################
app = Flask(__name__)

#dynamodb = boto3.resource(
#    'dynamodb',
#    endpoint_url=DYNAMO_ENDPOINT)

#create_songs_table(dynamodb)

@app.get('/')
def index():
    return 'Welcome to the Top Songs API. Try using /topsongs/<artist_code>'


@app.get('/topsongs/<artist_id>')
def top_songs(artist_id):
    redis_db = redis.Redis(port=REDIS_PORT)

    # Get query string and convert it to boolean
    use_cache = bool(strtobool(request.args.get('cache', default='true')))
   
    if use_cache:
        # Data is cached
        if redis_db.exists('top_songs_' + artist_id):
            print('Using cached data.')

            response = redis_db.get('top_songs_' + artist_id).decode()
            return response

        # Try retrieving data locally
        try:
            print('Trying to retrieve information locally.')

            #dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMO_ENDPOINT)
            #table = dynamodb.Table('popular_songs')
            #response = table.get_item(Key={'artist_id': artist_id})
            #response = response['Item']
            #cache_data(redis_db, response)
            #return json.dumps(response)

            # This is used only when dynamoDB is unavailable, otherwise comment this
            raise ClientError({'message': 'DynamoDB unavailable'}, -1)

        # Data is neither cached nor locally available
        except ClientError:
            print('Local database retrieval failed. Retrieving external information.')
            response = retrieve_external_response(artist_id)

            #persist_songs(
            #    response['transaction_id'], response['artist_id'],
            #    response['artist_name'], response['artist_songs'])

            cache_songs(redis_db, response)

            return json.dumps(response)
    
    else:
        print('Cache disabled. Retrieving external information')
        response = retrieve_external_response(artist_id)

        #persist_songs(
        #    response['transaction_id'], response['artist_id'],
        #    response['artist_name'], response['artist_songs'])

        return json.dumps(response)
