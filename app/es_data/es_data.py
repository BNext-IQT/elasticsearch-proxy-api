"""
Module that returns data from elascticsearch
"""
import json
import hashlib
import base64

from app.es_connection import ES
from app.cache import CACHE
from app.config import RUN_CONFIG


def get_es_response(index_name, es_query):
    """""
    :param index_name: name of the index to query against
    :param es_query: dict with the query to send
    :return: the dict with the response from es
    """

    cache_key = get_es_query_cache_key(index_name, es_query)
    cache_response = CACHE.get(key=cache_key)
    if cache_response is not None:
        return cache_response

    response = ES.search(index=index_name, body=es_query)

    seconds_valid = RUN_CONFIG.get('es_proxy_cache_seconds')
    CACHE.set(key=cache_key, value=response, timeout=seconds_valid)

    return response

def get_es_query_cache_key(index_name, es_query):
    """
    Produces a key to save the data in the cache based on the parameters given
    :param index_name: name of the index to query against
    :param es_query: dict with the query to send
    :return: the key to save the data in the cache
    """
    es_request_digest = get_es_request_digest(es_query)

    return f'{index_name}-{es_request_digest}'

def get_es_request_digest(es_query):
    """
    :param es_query: query sent to elasticsearch
    :return: a digest of the query
    """
    stable_raw_search_data = json.dumps(es_query, sort_keys=True)
    search_data_digest = hashlib.sha256(stable_raw_search_data.encode('utf-8')).digest()
    base64_search_data_hash = base64.b64encode(search_data_digest).decode('utf-8')

    return base64_search_data_hash
