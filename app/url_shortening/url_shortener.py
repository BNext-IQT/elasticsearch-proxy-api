"""
Module with the URL Shortening functions
"""
import hashlib
import base64
from datetime import datetime, timedelta

from app.es_data import es_data
from app.config import RUN_CONFIG
from app import app_logging
from app.usage_statistics import statistics_saver
from app.url_shortening.expired_urls_deletion import ExpiredURLsDeletionThread

class URLNotFoundError(Exception):
    """
    Error raises when an url was not found
    """
# ----------------------------------------------------------------------------------------------------------------------
# URL Shortening
# ----------------------------------------------------------------------------------------------------------------------

def shorten_url(long_url):
    """
    :param long_url:
    :return: an object with the hash and expiration date of the hash
    """
    hex_digest = hashlib.md5(long_url.encode('utf-8')).digest()

    # replace / and + to avoid routing problems
    url_hash = base64.b64encode(hex_digest).decode('utf-8').replace('/', '_').replace('+', '-')
    app_logging.debug(f'url_hash: {url_hash}')

    # check if the url has been shortened before
    raw_document = get_url_shortening(url_hash)
    already_exists = raw_document is not None

    if already_exists:

        app_logging.debug(f'already exists')

        keep_alive = RUN_CONFIG.get('url_shortening').get('keep_alive', False)
        if not keep_alive:
            expiration_timestamp = raw_document['_source']['expires']
            expires = datetime.fromtimestamp(expiration_timestamp / 1000)
            app_logging.debug(f'keep_alive is on, new expiration date is {expires}')
        else:
            expires = extend_expiration_date(raw_document)

    else:

        app_logging.debug(f'Did not exist before')

        expires = save_shortened_url(long_url, url_hash)

    statistics_saver.record_url_was_shortened()
    trigger_deletion_of_expired_urls()
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

    now = datetime.utcnow()
    time_delta = timedelta(days=RUN_CONFIG.get('url_shortening').get('days_valid'))
    expiration_date = now + time_delta
    expires = expiration_date.timestamp() * 1000

    index_name = RUN_CONFIG.get('url_shortening').get('index_name')

    document = {
        'long_url': long_url,
        'hash': url_hash,
        'expires': expires,
        'creation_date_2': int(now.timestamp() * 1000)
    }

    dry_run = RUN_CONFIG.get('url_shortening').get('dry_run')
    if dry_run:
        app_logging.debug(f'Dry run is true, not saving the document {document} to the index {index_name}')
    else:
        es_data.save_es_doc(index_name, document)

    return expiration_date


# ----------------------------------------------------------------------------------------------------------------------
# URL Expansion
# ----------------------------------------------------------------------------------------------------------------------
def expand_url(url_hash):
    """
    :param url_hash: hash of the url to expand
    :return: the expanded url corresponding to the hash
    """
    raw_document = get_url_shortening(url_hash)
    if raw_document is None:
        raise URLNotFoundError(f'No url correspond to the hash {url_hash}')


def extend_expiration_date(raw_document):
    """
    extends the expiration date of the url_shortening document
    :param raw_document: raw document obtained
    :return: the new expiration date
    """
    old_expires = raw_document['_source']['expires']
    old_expiration_date = datetime.fromtimestamp(old_expires / 1000)

    last_time_extended = raw_document['_source'].get('last_time_extended')
    if last_time_extended is not None:
        last_time_extended_date = datetime.fromtimestamp(last_time_extended / 1000)

        now = datetime.utcnow()
        time_since_last_extended = now - last_time_extended_date
        hours_since_last_extended = int(time_since_last_extended.seconds / 3600)
        if hours_since_last_extended < 1:
            return old_expiration_date

    time_delta = timedelta(days=RUN_CONFIG.get('url_shortening').get('keep_alive_days'))
    new_expiration_date = old_expiration_date + time_delta

    times_extended = raw_document['_source'].get('times_extended', 0)
    times_extended += 1

    doc_id = raw_document['_id']
    index_name = RUN_CONFIG.get('url_shortening').get('index_name')

    updated_fields = {
        'doc': {
            'expires': int(new_expiration_date.timestamp() * 1000),
            'times_extended': times_extended,
            'last_time_extended': int(datetime.utcnow().timestamp() * 1000),
        }
    }

    es_data.update_es_doc(index_name=index_name, updated_fields=updated_fields, doc_id=doc_id)

    return new_expiration_date


def get_url_shortening(url_hash):
    """
    :param url_hash: hash of the url to look for
    :return: url shortening dict from elasticsearch
    """

    index_name = RUN_CONFIG.get('url_shortening').get('index_name')
    es_query = {
        "query": {
            "query_string": {
                "query": url_hash,
                "default_field": "hash"
            }
        }
    }

    shortening_response = es_data.get_es_response(index_name, es_query, ignore_cache=True)
    total_hits = shortening_response['hits']['total']['value']
    app_logging.debug(f'total_hits {total_hits}')

    if shortening_response['hits']['total']['value'] == 0:
        return None

    raw_document = shortening_response['hits']['hits'][0]
    return raw_document


# ----------------------------------------------------------------------------------------------------------------------
# Deletion of old records
# ----------------------------------------------------------------------------------------------------------------------
def trigger_deletion_of_expired_urls():
    """
    Triggers the deletion of old shortened urls records
    """
    print('trigger_deletion_of_expired_urls')
    deletion_thread = ExpiredURLsDeletionThread()
    deletion_thread.start()
