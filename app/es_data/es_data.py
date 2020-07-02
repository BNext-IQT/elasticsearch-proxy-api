"""
Module that returns data from elascticsearch
"""
import json
import hashlib
import base64
import time

import elasticsearch

from app.es_connection import ES
from app import cache
from app.config import RUN_CONFIG
from app import app_logging
from app.usage_statistics import statistics_saver


class ESDataNotFoundError(Exception):
    """Base class for exceptions in this file."""


def get_es_response(index_name, es_query):
    """""
    :param index_name: name of the index to query against
    :param es_query: dict with the query to send
    :return: the dict with the response from es
    """

    cache_key = get_es_query_cache_key(index_name, es_query)
    app_logging.debug(f'cache_key: {cache_key}')

    start_time = time.time()
    cache_response = cache.fail_proof_get(key=cache_key)
    if cache_response is not None:
        end_time = time.time()
        time_taken = end_time - start_time
        app_logging.debug(f'results were cached')
        record_that_response_was_cached(index_name, es_query, time_taken)
        return cache_response

    app_logging.debug(f'results were not cached')

    try:

        start_time = time.time()
        response = ES.search(index=index_name, body=es_query)
        end_time = time.time()
        time_taken = end_time - start_time

        record_that_response_not_cached(index_name, es_query, time_taken)

    except elasticsearch.exceptions.RequestError as error:
        app_logging.error(f'This query caused an error: ')
        app_logging.error(f'index_name:{index_name}')
        app_logging.error(f'es_query:')
        app_logging.error(es_query)
        raise error

    seconds_valid = RUN_CONFIG.get('es_proxy_cache_seconds')
    cache.fail_proof_set(key=cache_key, value=response, timeout=seconds_valid)

    return response


def do_multisearch(body):
    """
    :param body: body of the multisearch
    :return: the result of the multisearch
    """
    cache_key = get_multisearch_cache_key(body)
    app_logging.debug(f'cache_key: {cache_key}')

    start_time = time.time()
    cache_response = cache.fail_proof_get(key=cache_key)
    if cache_response is not None:
        end_time = time.time()
        time_taken = end_time - start_time
        app_logging.debug(f'results were cached')
        record_that_response_was_cached('multisearch', {'query':body}, time_taken)
        return cache_response

    app_logging.debug(f'results were not cached')

    start_time = time.time()
    result = ES.msearch(body=body)
    end_time = time.time()
    time_taken = end_time - start_time

    record_that_response_not_cached('multisearch', {'query':body}, time_taken)

    seconds_valid = RUN_CONFIG.get('es_proxy_cache_seconds')
    cache.fail_proof_set(key=cache_key, value=result, timeout=seconds_valid)

    return result


def get_es_doc(index_name, doc_id):
    """
    :param index_name: name of the intex to which the document belongs
    :param doc_id: id of the document
    :return: the dict with the response from es corresponding to the document
    """

    cache_key = f'document-{doc_id}'
    app_logging.debug(f'cache_key: {cache_key}')

    equivalent_query = {
        "query": {
            "ids": {
                "values": doc_id
            }
        }
    }

    start_time = time.time()
    cache_response = cache.fail_proof_get(key=cache_key)
    if cache_response is not None:
        end_time = time.time()
        time_taken = end_time - start_time
        app_logging.debug(f'results were cached')
        record_that_response_was_cached(index_name, equivalent_query, time_taken)
        return cache_response

    app_logging.debug(f'results were not cached')

    try:
        start_time = time.time()
        response = ES.get(index=index_name, id=doc_id)
        end_time = time.time()
        time_taken = end_time - start_time

        record_that_response_not_cached(index_name, equivalent_query, time_taken)
    except elasticsearch.exceptions.NotFoundError as error:
        raise ESDataNotFoundError(repr(error))

    seconds_valid = RUN_CONFIG.get('es_proxy_cache_seconds')
    cache.fail_proof_set(key=cache_key, value=response, timeout=seconds_valid)

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


def get_multisearch_cache_key(body):
    """
    :param body: body of the multisearch
    :return: the key to save the data in the cache
    """

    stable_raw_body = json.dumps(body, sort_keys=True)
    body_digest = hashlib.sha256(stable_raw_body.encode('utf-8')).digest()
    base64_hash = base64.b64encode(body_digest).decode('utf-8')

    return f'multisearch-{base64_hash}'


def get_es_request_digest(es_query):
    """
    :param es_query: query sent to elasticsearch
    :return: a digest of the query
    """
    stable_raw_search_data = json.dumps(es_query, sort_keys=True)
    search_data_digest = hashlib.sha256(stable_raw_search_data.encode('utf-8')).digest()
    base64_search_data_hash = base64.b64encode(search_data_digest).decode('utf-8')

    return base64_search_data_hash


def record_that_response_was_cached(index_name, es_query, time_taken):
    """
    Records that a response was already cached
    :param index_name: name of the index queried
    :param es_query: the query sent
    :param time_taken: time taken (seconds) to get the data
    """
    es_request_digest = get_es_request_digest(es_query)
    is_cached = True
    statistics_saver.save_index_usage_record(index_name, es_query, es_request_digest, is_cached, time_taken)


def record_that_response_not_cached(index_name, es_query, time_taken):
    """
    Records that a response was not cached
    :param index_name: name of the index queried
    :param es_query: the query sent
    :param time_taken: time taken (seconds) to get the data
    """
    es_request_digest = get_es_request_digest(es_query)
    is_cached = False
    statistics_saver.save_index_usage_record(index_name, es_query, es_request_digest, is_cached, time_taken)
