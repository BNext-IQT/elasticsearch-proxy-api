"""
Module that loads contexts from results
"""
import re

import requests

from app.config import RUN_CONFIG
from app.cache import CACHE
from app import app_logging


class ContextLoaderError(Exception):
    """Base class for exceptions in this module."""


WEB_RESULTS_SIZE_LIMIT = RUN_CONFIG.get('filter_query_max_clauses')


def get_context_url(context_dict):
    """
    returns the url for loading the context
    :param context_dict: dict describing the context
    """
    host = re.search(r'[^/]+\.ebi\.ac\.uk(:\d+)?', context_dict["delayed_jobs_base_url"]).group(0)
    host_mappings = RUN_CONFIG.get('delayed_jobs', {}).get('server_mapping', {})
    mapped_host = host_mappings.get(host)
    mapped_base_url = context_dict['delayed_jobs_base_url'].replace(host, mapped_host)

    return f'{mapped_base_url}/outputs/{context_dict["context_id"]}/results.json'


def get_context(context_dict):
    """
    Returns the context described by the context dict
    :param context_dict: dictionary describing the context
    :return: the context loaded as an object
    """
    context_url = get_context_url(context_dict)
    app_logging.debug(f'Loading context from url: {context_url}')
    context_request = requests.get(context_url)

    if context_request.status_code != 200:
        raise ContextLoaderError('There was an error while loading the context: ' + context_request.text)

    results = context_request.json()['search_results']

    total_results = len(results)
    if total_results > WEB_RESULTS_SIZE_LIMIT:
        results = results[0:WEB_RESULTS_SIZE_LIMIT]

    return results, total_results


def load_context_index(context_id, id_property, context):
    """
    Loads an index based on the id property of the context, for fast access
    :param context_id: id of the context loaded
    :param id_property: property used to identify each item
    :param context: context loaded
    :return:
    """

    context_index_key = 'context_index-{}'.format(context_id)
    context_index = CACHE.get(key=context_index_key)
    if context_index is None:
        context_index = {}

        for index, item in enumerate(context):
            context_index[item[id_property]] = item
            context_index[item[id_property]]['index'] = index

        CACHE.set(key=context_index_key, value=context_index, timeout=3600)

    return context_index
