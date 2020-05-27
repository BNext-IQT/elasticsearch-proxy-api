"""
Service that handles the general requests to elasticsearch data
"""
import json

from app import app_logging
from app.es_data import es_data
from app.context_loader import context_loader
from app.config import RUN_CONFIG
from app.es_data import es_mappings

CONTEXT_PREFIX = '_context'


class ESProxyServiceError(Exception):
    """Base class for exceptions in this file."""


def get_es_data(index_name, raw_es_query, raw_context, raw_contextual_sort_data):
    """
    :param index_name: name of the index to query
    :param raw_es_query: stringifyied version of the query to send to elasticsearch
    :param raw_context: stringifyied version of a JSON object describing the context of the query
    :param id_property: property that identifies every item. Required when context provided
    :param raw_contextual_sort_data: description of sorting if sorting by contextual properties
    :return: Returns the json response from elasticsearch and some metadata if necessary
    """
    if raw_context is None:
        app_logging.debug('No context detected')
        es_query = json.loads(raw_es_query)
        es_response = es_data.get_es_response(index_name, es_query)
        response = {
            'es_response': es_response,
        }
        return response

    app_logging.debug(f'Using context: {raw_context}')
    es_response, metadata = get_items_with_context(index_name, raw_es_query, raw_context, raw_contextual_sort_data)

    response = {
        'es_response': es_response,
        'metadata': metadata
    }
    return response


def get_items_with_context(index_name, raw_es_query, raw_context, raw_contextual_sort_data='{}'):
    """
    :param index_name: name of the index to query
    :param raw_es_query: es_query stringifyied
    :param raw_context: context dict stringifyied
    :param raw_contextual_sort_data:
    :return: the items in the es_query with the context given in the context description
    """

    context_dict = json.loads(raw_context)
    context, total_results = context_loader.get_context(context_dict)

    id_properties = es_mappings.get_id_properties_for_index(index_name)
    # create a context index so access is faster
    context_id = context_dict['context_id']
    context_index = context_loader.load_context_index(context_id, id_properties, context)

    if raw_contextual_sort_data is not None:
        contextual_sort_data = json.loads(raw_contextual_sort_data)
    else:
        contextual_sort_data = {}

    search_data_with_injections = get_search_data_with_injections(raw_es_query, contextual_sort_data, id_properties,
                                                                  total_results, context_index)
    raw_search_data_with_injections = json.dumps(search_data_with_injections)
    es_response = es_data.get_es_response(index_name, json.loads(raw_search_data_with_injections))
    add_context_values_to_response(es_response, context_index)

    metadata = {
        'total_results': len(context_index),
        'max_results_injected': RUN_CONFIG.get('filter_query_max_clauses')
    }
    return es_response, metadata


def get_search_data_with_injections(raw_es_query, contextual_sort_data, id_properties, total_results, context_index):
    """
    :param raw_es_query: stringifyed version of the es query
    :param contextual_sort_data: dict describing the sorting by contextual properties
    :param id_properties: property used to identity each item
    :param total_results: total number of results
    :param context_index: index with the context
    :return: the query to send to elasticsearch
    """

    parsed_search_data = json.loads(raw_es_query)
    scores_query = get_scores_query(contextual_sort_data, id_properties, total_results, context_index)
    parsed_search_data['query']['bool']['must'].append(scores_query)

    ids_list = list(context_index.keys())
    ids_query = get_request_for_chembl_ids(id_properties, ids_list)
    parsed_search_data['query']['bool']['filter'].append(ids_query)

    return parsed_search_data


def add_context_values_to_response(es_response, context_index):
    """
    adds the values of the context to the response of es
    :param es_response: response without the context values
    :param context_index: index of the context values
    """

    hits = es_response['hits']['hits']
    for hit in hits:
        hit_id = hit['_id']
        context_obj = context_index[hit_id]
        hit['_source'][CONTEXT_PREFIX] = context_obj


def get_scores_query(contextual_sort_data, id_properties, total_results, context_index):
    """
    Returns the query with the scores for the data to sort it with the contextual properties.
    IT DOES NOT SUPPORT MULTIPLE ID PROPERTIES
    :param contextual_sort_data: dict describing the sorting by contextual properties
    :param id_properties: property used to identity each item
    :param total_results: total number of results
    :param context_index: index with the context
    """
    id_property = id_properties[0]
    contextual_sort_data_keys = contextual_sort_data.keys()
    if len(contextual_sort_data_keys) == 0:
        # if nothing is specified use the default scoring script, which is to score them according to their original
        # position in the results
        score_property = 'index'
        score_script = f'String id=doc["{id_property}"].value; ' \
                       f'return {str(total_results)} - params.scores[id]["{score_property}"];'
    else:

        raw_score_property = list(contextual_sort_data_keys)[0]
        score_property = raw_score_property.replace('{}.'.format(CONTEXT_PREFIX), '')
        sort_order = contextual_sort_data[raw_score_property]

        if sort_order == 'desc':
            score_script = "String id=doc['" + id_property + "'].value; " \
                                                             "return params.scores[id]['" + score_property + "'];"
        else:
            score_script = "String id=doc['" + id_property + "'].value; " \
                                                             "return 1 / params.scores[id]['" + score_property + "'];"

    scores_query = {
        'function_score': {
            'functions': [{
                'script_score': {
                    'script': {
                        'lang': "painless",
                        'params': {
                            'scores': context_index,
                        },
                        'source': score_script
                    }
                }
            }]
        }
    }

    return scores_query


def get_request_for_chembl_ids(id_properties, ids_list):
    """
    creates a terms query with the ids given as a parameter for the id_property given as parameter
    IT DOES NOT SUPPORT MULTIPLE ID PROPERTIES
    :param id_properties: property that identifies the items
    :param ids_list: list of ids to query
    :return: the terms query to use
    """
    id_property = id_properties[0]
    query = {
        'terms': {
            id_property: ids_list
        }
    }

    return query
