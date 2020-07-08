"""
Module that provides a Thread to delete old records from elasticsearch
"""
import threading
import random
from datetime import datetime, timezone, timedelta

from elasticsearch.helpers import scan

from app import app_logging
from app.config import RUN_CONFIG
from app.es_monitoring_connection import ES_MONITORING

BULK_SIZE = 100


class OldMonitoringRecordsDeletionThread(threading.Thread):
    """
    Class that implements a thread to delete the old records of elasticsearch
    """

    def __init__(self):
        threading.Thread.__init__(self, )
        app_logging.info('Initialising thread to delete old monitoring records')

    def run(self):
        dice = random.randint(0, 1000)
        dice_must_be = 0
        do_this = dice == dice_must_be
        if not do_this:
            app_logging.info(f'Not trying to delete expired urls. Dice was {dice}. Must be {dice_must_be}')
            return

        indexes_and_timestamps = RUN_CONFIG.get('lazy_old_record_deletion').get('index_names_and_timestamps')

        for config in indexes_and_timestamps:
            days_old = RUN_CONFIG.get('lazy_old_record_deletion').get('delete_records_older_than_days')

            for current_days_old in range(680, days_old, -1):

                app_logging.info(f'---')
                delete_old_index_data(config['index_name'], config['timestamp_field'], current_days_old)
                app_logging.info(f'---')


def delete_old_index_data(index_name, timestamp_field, days_old):
    """
    Deletes the old data of the index given as parameter
    :param index_name: name of the index for which to delete the old data
    :param timestamp_field: field to be used to consider the record as old
    :param days_old: how many days old must the records be to be deleted
    """

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    time_delta = timedelta(days=days_old)
    expiration_date = now - time_delta

    app_logging.info(
        f'Deleting old index data of index {index_name} using field {timestamp_field} that are older than '
        f'{expiration_date} ({days_old} days old)')

    query = {

        "query": {
            "range": {
                f'{timestamp_field}': {
                    "lte": str(int(expiration_date.timestamp() * 1000))
                }

            }
        }
    }
    app_logging.info(f'index_name: {index_name}')
    app_logging.info(f'query: {query}')

    expired_docs_response = ES_MONITORING.search(index=index_name, body=query)
    num_items = expired_docs_response['hits']['total']['value']
    max_items = RUN_CONFIG.get('lazy_old_record_deletion').get('expired_docs_lazy_deletion_threshold')
    must_do_deletion = num_items > max_items

    app_logging.info(f'there are {num_items} old records in {index_name}')

    if must_do_deletion:

        # pylint: disable=unexpected-keyword-arg
        app_logging.info('Deleting!!!')
        ES_MONITORING.delete_by_query(index=index_name, body=query, conflicts='proceed')
        app_logging.info(f'Deleted {num_items} monitoring records olddr than {expiration_date} in index {index_name}')

    else:
        app_logging.info(
            f'Not deleting expired docs of because there are just {num_items}, '
            f'will do deletion when more than {max_items}')


def stream_items_for_deletion(query, index_name):
    """
    :param index_name: name of the index on which to execute the query
    :param query: query for the stream
    :return: the items as they are iterated to be deleted
    """

    for doc_i in scan(ES_MONITORING, query=query, index=index_name, scroll='1m'):
        del doc_i['_score']
        doc_i['_op_type'] = 'delete'
        yield doc_i
