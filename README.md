# TOP SONGS API

Welcome to Top Songs API. You can get the 10 most popular songs of an artist.

## !!! Disclaimer !!!
As I couldn't get access to AWS DynamoDB, parts of the code with calls to the platform were left commented and couldn't be completely tested. Application is intended to work fine with Redis caching.

### Setup

This setup helper assumes you have python 3, aws-cli and redis previously installed and running on your machine.

- Install required libraries
> pip3 install -r requirements.txt

- Export required environment variables
> EXPORT FLASK_APP=top_songs

> EXPORT ACCESS_TOKEN=\<your genius API access token\>

> EXPORT DYNAMO_ENDPOINT=\<your dynamo endpoint (host:port)\>

> EXPORT REDIS_PORT=\<your redis port\>

- Run Flask APP
> flask run


### Endpoints
| Endpoint | Result |
|---|---|
|**topsongs/<artist_id>**| Returns the top 10 songs of the given artist. Optional arguments: cache (true\|false)|

