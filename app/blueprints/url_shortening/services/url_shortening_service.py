"""
URL Shortening Service
"""
import hashlib
import base64
from datetime import datetime, timedelta

from app.es_data import es_data
from app.config import RUN_CONFIG
from app import app_logging
from app.usage_statistics import statistics_saver


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

    print('checking if it exists')
    # check if the url has been shortened before
    index_name = RUN_CONFIG.get('url_shortening').get('index_name')
    es_query = {
        "query": {
            "query_string": {
                "query": url_hash,
                "default_field": "hash"
            }
        }
    }

    print('index_name: ', index_name)
    print('es_query: ', es_query)

    shortening_response = es_data.get_es_response(index_name, es_query)
    print('shortening_response: ', shortening_response)
    already_exists = shortening_response['hits']['total']['value'] != 0
    print('already_exists: ', already_exists)

    if already_exists:

        print('already exists')
        raw_document = shortening_response['hits']['hits'][0]
        keep_alive = RUN_CONFIG.get('url_shortening').get('keep_alive', False)
        if not keep_alive:
            expiration_timestamp = raw_document['_source']['expires']
            expires = datetime.utcfromtimestamp(expiration_timestamp / 1000)
        else:
            expires = extend_expiration_date(raw_document)

    else:

        expires = save_shortened_url(long_url, url_hash)

    statistics_saver.record_url_was_shortened()
    return {
        'hash': url_hash,
        'expires': expires
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

    index_name = RUN_CONFIG.get('url_shortening').get('index_name')

    document = {
        'long_url': long_url,
        'hash': url_hash,
        'expires': expires,
        'creation_date': now.timestamp() * 1000
    }

    dry_run = RUN_CONFIG.get('url_shortening').get('dry_run')
    if dry_run:
        app_logging.debug(f'Dry run is true, not saving the document {document} to the index {index_name}')
    else:
        es_data.save_es_doc(index_name, document)

    return expiration_date


def extend_expiration_date(raw_document):
    """
    extends the expiration date of the url_shortening document
    :param raw_document: raw document obtained
    :return: the new expiration date
    """

    old_expires = raw_document['_source']['expires']
    old_expiration_date = datetime.utcfromtimestamp(old_expires / 1000)

    time_delta = timedelta(days=RUN_CONFIG.get('url_shortening').get('keep_alive_days'))
    new_expiration_date = old_expiration_date + time_delta

    times_extended = raw_document['_source'].get('times_extended', 0)
    times_extended += 1

    doc_id = raw_document['_id']
    index_name = RUN_CONFIG.get('url_shortening').get('index_name')

    updated_fields = {
        'doc': {
            'expires': new_expiration_date.timestamp() * 1000,
            'times_extended': times_extended
        }
    }

    es_data.update_es_doc(index_name=index_name, updated_fields=updated_fields, doc_id=doc_id)

    return new_expiration_date
