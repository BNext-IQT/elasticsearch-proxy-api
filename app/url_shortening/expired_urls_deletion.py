"""
Module that provides a Thread to delete expired shortened urls
"""
import threading
import random
from datetime import datetime, timezone

from elasticsearch.helpers import scan, bulk

from app import app_logging
from app.config import RUN_CONFIG
from app.es_data import es_data
from app.es_connection import ES
from app.usage_statistics import statistics_saver

BULK_SIZE = 1000


class ExpiredURLsDeletionThread(threading.Thread):
    """
    Class that implements a thread to delete the old records of elasticsearch
    """

    def __init__(self):

        threading.Thread.__init__(self, )
        app_logging.debug('Initialising thread to delete expired urls')

    def run(self):

        dice = random.randint(0, 9)
        do_this = dice in [0, 1, 2]
        if not do_this:
            app_logging.debug(f'Not trying to delete expired urls. Dice was {dice}')
            return

        now = datetime.utcnow().replace(tzinfo=timezone.utc)

        index_name = RUN_CONFIG.get('url_shortening').get('index_name')
        query = {

            "query": {
                "range": {
                    "expires": {
                        "lte": str(int(now.timestamp() * 1000))
                    }

                }
            }
        }

        expired_urls_response = es_data.get_es_response(index_name, query, ignore_cache=True)

        num_items = expired_urls_response['hits']['total']['value']
        max_items = RUN_CONFIG.get('url_shortening').get('expired_urls_lazy_deletion_threshold')
        must_do_deletion = num_items > max_items

        if must_do_deletion:

            bulk(ES, stream_items_for_deletion(query, index_name), chunk_size=BULK_SIZE)
            app_logging.info(f'Deleted {num_items} expired shortened urls.')
            statistics_saver.record_expired_urls_were_deleted()

        else:
            app_logging.debug(
                f'Not deleting expired urls because there are just {num_items}, '
                f'will do deletion when more than {max_items}')


def stream_items_for_deletion(query, index_name):
    """
    :param index_name: name of the index on which to execute the query
    :param query: query for the stream
    :return: the items as they are iterated to be deleted
    """

    for doc_i in scan(ES, query=query, index=index_name, scroll='1m'):
        del doc_i['_score']
        doc_i['_op_type'] = 'delete'
        yield doc_i
