"""
URL Shortening Service
"""
import hashlib
import base64
from datetime import datetime, timedelta

from app.es_data import es_data
from app.config import RUN_CONFIG


class URLShorteningError(Exception):
    """
    Class for errors in this module
    """


def shorten_url(long_url):
    """
    :param long_url:
    :return: an object with the hash and expiration date of the hash
    """

    hex_digest = hashlib.md5(long_url.encode('utf-8')).digest()

    # replace / and + to avoid routing problems
    url_hash = base64.b64encode(hex_digest).decode('utf-8').replace('/', '_').replace('+', '-')
    print('url_hash: ', url_hash)

    # check if the url has been shortened before
    index_name = RUN_CONFIG.get('url_shortening').get('index_name')
    es_query = {
        "query": {
            "terms": {
                "_id": ["7Vj59yCHzqkB4OhGt4z3xg=="]
            }
        }
    }

    shortening_response = es_data.get_es_response(index_name, es_query)
    print('shortening_response: ', shortening_response)
    already_exists = shortening_response['hits']['total']['value'] != 0
    print('already_exists: ', already_exists)

    if already_exists:

        print('already exists')

    else:

        save_shortened_url(long_url, url_hash)

    return {
        'hash': 'aaa',
        'expires': 'tomorrow'
    }


def save_shortened_url(long_url, url_hash):
    """
    Saves the shortened url to es
    :param long_url: full url to save
    :param url_hash: hash of the url
    """

    now = datetime.now()
    time_delta = timedelta(days=RUN_CONFIG.get('url_shortening').get('days_valid'))
    expiration_date = now + time_delta
    expires = expiration_date.timestamp() * 1000
    print('expires: ', expires)


