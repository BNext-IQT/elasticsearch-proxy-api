"""
Module that loads contexts from results
"""
import re

import requests

from app.config import RUN_CONFIG
from app import cache
from app import app_logging

from utils import id_properties


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

    # Make sure to always use http because connection is internal
    scheme = re.search(r'^http(s)?://', mapped_base_url).group(0)
    if scheme is None:
        mapped_base_url = f'http://{mapped_base_url}'
    else:
        mapped_base_url = mapped_base_url.replace(scheme, 'http://')

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


def load_context_index(context_id, id_properties_list, context):
    """
    Loads an index based on the id property of the context, for fast access
    :param context_id: id of the context loaded
    :param id_properties_list: property used to identify each item
    :param context: context loaded
    :return:
    """

    context_index_key = 'context_index-{}'.format(context_id)
    context_index = cache.fail_proof_get(context_index_key)
    if context_index is None:
        context_index = {}

        for index_number, item in enumerate(context):
            id_value = id_properties.get_id_value(id_properties_list, item)
            context_index[id_value] = item
            context_index[id_value]['index'] = index_number

        cache.fail_proof_set(context_index_key, context_index, 3600)

    return context_index
