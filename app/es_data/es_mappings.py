"""
Module that returns mapping data from elascticsearch
"""
from app.es_connection import ES
from app import app_logging
from app.es_data import utils
from utils import dict_property_access

SIMPLE_MAPPINGS = {
    'keyword': 'string',
    'text': 'string',
    'completion': 'string-es-interal',
    'float': 'double',
    'double': 'double',
    'byte': 'integer',
    'short': 'integer',
    'integer': 'integer',
    'long': 'integer',
    'boolean': 'boolean',
    'date': 'date',
    'object': 'object'
}

AGGREGATABLE_TYPES = {'boolean', 'byte', 'short', 'integer', 'long', 'float', 'double', 'keyword', 'lower_case_keyword'}


class EsMappingsError(Exception):
    """Base class for exceptions in the ES Mappings"""


def get_simplified_property_mapping(index_name, property_id):
    """
    :param index_name: index name where the property belongs
    :param property_id: id of the property to check
    :return: a dict with the mappings of the property in the index given as parameter
    """
    app_logging.debug(f'Getting mapping of {property_id} in {index_name}')
    index_mapping = get_index_mapping(index_name)
    property_accessor = property_id.replace('.', '.properties.')
    property_raw_mapping = dict_property_access.get_property_value(index_mapping, property_accessor)

    if property_raw_mapping is None:
        return None

    label, label_mini = utils.get_labels_from_property_name(index_name, property_id)

    simplified_mapping = {
        'type': get_simplified_property_type(property_raw_mapping),
        'aggregatable': get_simplified_property_aggregatability(property_raw_mapping),
        'label': label,
        'label_mini': label_mini
    }

    return simplified_mapping

def get_index_mapping(index_name):
    """
    :param index_name: name of the index to check
    :return: full mapping of an index
    """
    raw_index_mapping = ES.indices.get_mapping(index=index_name)
    index_mapping = raw_index_mapping.get(list(raw_index_mapping.keys())[0])['mappings']['properties']
    return index_mapping

def get_simplified_property_type(property_mapping):
    """
    :param property_mapping: mapping dict from the ES response
    :return: a simplified type of the property
    """
    es_type = get_es_property_type(property_mapping)
    simplified_type = SIMPLE_MAPPINGS.get(es_type)

    if simplified_type is None:
        raise EsMappingsError(f'There is no simplified type mapped to ES mapping: {es_type}')

    return simplified_type


def get_es_property_type(property_mapping):
    """
    :param property_mapping: mapping dict from the ES response
    :return: ES type of the property
    """
    es_type = property_mapping.get('type')
    if es_type is None:
        return 'object'

    return es_type


def get_simplified_property_aggregatability(property_mapping):
    """
    :param property_mapping: mapping dict from the ES response
    :return: whether the property is aggregatable or not
    """
    es_type = get_es_property_type(property_mapping)
    return es_type in AGGREGATABLE_TYPES
