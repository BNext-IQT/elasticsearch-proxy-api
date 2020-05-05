"""
Module that saves statistics in elasticsearch
"""
import json

def get_index_usage_record_dict(es_index, es_full_query, es_request_digest, is_cached, request_date, run_env_type):
    """
    :param es_index: index used in the request
    :param es_full_query: full query sent requested
    :param es_request_digest: digest of the request
    :param is_cached: whether the data was cached or not
    :param request_date: timestamp for the request date
    :param run_env_type: type of run environment
    :return: a dict to be used to save the cache statistics in the elasticsearch index
    """

    es_query = json.dumps(es_full_query.get('query', None))
    es_aggs = json.dumps(es_full_query.get('aggs', None))

    print(es_request_digest)
    print(is_cached)
    print(request_date)
    print(run_env_type)

    return {
        'es_index': es_index,
        'es_query': es_query,
        'es_aggs': es_aggs
    }
