"""
Service that handles the general requests to elasticsearch data
"""
import json

from app import app_logging
from app.es_data import es_data

class ESProxyServiceError(Exception):
    """Base class for exceptions in this file."""


def get_es_data(index_name, raw_es_query, raw_context, id_property, raw_contextual_sort_data):
    """
    :param index_name: name of the index to query
    :param raw_es_query: stringifyied version of the query to send to elasticsearch
    :param raw_context: stringifyied version of a JSON object describing the context of the query
    :param id_property: property that identifies every item. Required when context provided
    :param raw_contextual_sort_data: description of sorting if sorting by contextual properties
    :return: Returns the json response from elasticsearch
    """
    if raw_context is None:

        app_logging.debug('No context detected')
        es_query = json.loads(raw_es_query)
        return es_data.get_es_response(index_name, es_query)

    else:

        return {'msg': 'hola'}



