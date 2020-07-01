"""
Module that saves statistics in elasticsearch
"""
import json
from datetime import datetime

from app.config import RUN_CONFIG
from app.config import ImproperlyConfiguredError
from app import app_logging
from app.es_monitoring_connection import ES_MONITORING


def get_index_usage_record_dict(es_index, es_full_query, es_request_digest, is_cached, request_date, run_env_type,
                                time_taken):
    """
    :param es_index: index used in the request
    :param es_full_query: full query sent requested
    :param es_request_digest: digest of the request
    :param is_cached: whether the data was cached or not
    :param request_date: timestamp for the request date
    :param run_env_type: type of run environment
    :param time_taken: time taken (seconds) to get the data
    :return: a dict to be used to save the cache statistics in the elasticsearch index
    """

    es_query = json.dumps(es_full_query.get('query', None))
    es_aggs = json.dumps(es_full_query.get('aggs', None))

    return {
        'es_index': es_index,
        'es_query': es_query,
        'es_aggs': es_aggs,
        'es_request_digest': es_request_digest,
        'is_cached': is_cached,
        'request_date': request_date,
        'run_env_type': run_env_type,
        'time_taken': time_taken
    }


def save_index_usage_record(es_index, es_full_query, es_request_digest, is_cached, time_taken):
    """
    Saves the job record in elasticsearch with the parameters given
    :param es_index: index used in the request
    :param es_full_query: full query sent requested
    :param es_request_digest: digest of the request
    :param is_cached: whether the data was cached or not
    :return: a dict to be used to save the cache statistics in the elasticsearch index
    :param time_taken: time taken (seconds) to get the data
    """

    request_date = datetime.now().timestamp() * 1000
    run_env_type = RUN_CONFIG.get('run_env')

    cache_record_dict = get_index_usage_record_dict(es_index, es_full_query, es_request_digest, is_cached, request_date,
                                                    run_env_type, time_taken)

    index_name = RUN_CONFIG.get('usage_statistics').get('cache_statistics_index')

    if index_name is None:
        raise ImproperlyConfiguredError('You must provide an index name to save job statistics in'
                                        ' job_statistics.general_statistics_index')

    save_record_to_elasticsearch(cache_record_dict, index_name)


def save_free_text_search_record(time_taken):
    """
    saves the record in the monitorint elasticsearch with the parameters given
    :param time_taken: time taken to process the search
    """
    print('SAVE FREE TEXT SEARCH: ', time_taken)

# ----------------------------------------------------------------------------------------------------------------------
# Saving records to elasticsearch
# ----------------------------------------------------------------------------------------------------------------------
def save_record_to_elasticsearch(doc, index_name):
    """
    Saves the record indicated as parameter to the index indicated as parameter
    :param doc: doc to save
    :param index_name: index where to save the dod
    """

    dry_run = RUN_CONFIG.get('usage_statistics', {}).get('dry_run', False)
    es_host = RUN_CONFIG.get('usage_statistics', {}).get('elasticsearch', {}).get('host')
    es_port = RUN_CONFIG.get('usage_statistics', {}).get('elasticsearch', {}).get('port')

    if dry_run:
        app_logging.debug(f'Not actually sending the record to the statistics index {index_name} (dry run): {doc}')
    else:
        app_logging.debug(f'Sending the following record to the statistics: {doc} '
                          f'index name: {index_name} es_host: {es_host}:{es_port}')

        result = ES_MONITORING.index(index=index_name, body=doc, doc_type='_doc')
        app_logging.debug(f'Result {result}')
