"""
Module that saves statistics in elasticsearch
"""
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

    es_query = es_full_query.get('query', None)
    es_aggs = es_full_query.get('aggs', None)

    return {}
