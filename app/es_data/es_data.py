"""
Module that returns data from elascticsearch
"""
import json
import hashlib
import base64

from app.es_connection import ES


def get_es_response(index_name, es_query):
    """""
    :param index_name: name of the index to query against
    :param es_query: dict with the query to send
    :return: the dict with the response from es
    """

    response = ES.search(index=index_name, body=es_query)
    return response


def get_es_query_cache_key(index_name, es_query):
    """
    Produces a key to save the data in the cache based on the parameters given
    :param index_name: name of the index to query against
    :param es_query: dict with the query to send
    :return: the key to save the data in the cache
    """

    stable_raw_search_data = json.dumps(es_query, sort_keys=True)
    search_data_digest = hashlib.sha256(stable_raw_search_data.encode('utf-8')).digest()
    base64_search_data_hash = base64.b64encode(search_data_digest).decode('utf-8')

    return f'{index_name}-{base64_search_data_hash}'
