"""
Module that returns mapping data from elascticsearch
"""
from app.es_connection import ES
from app import app_logging
from app.es_data import utils

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
    'date': 'date'
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
    full_mapping = ES.indices.get_field_mapping(index=index_name, fields=property_id)
    mappings = full_mapping[list(full_mapping.keys())[0]]['mappings']

    print('mappings: ')
    print(mappings)
    property_mapping = mappings.get(property_id)
    if property_mapping is None:
        return None

    label, label_mini = utils.get_labels_from_property_name(index_name, property_id)

    simplified_mapping = {
        'type': get_simplified_property_type(property_mapping),
        'aggregatable': get_simplified_property_aggregatability(property_mapping),
        'label': label,
        'label_mini': label_mini
    }

    print('simplified_mapping: ')
    print(simplified_mapping)
    return simplified_mapping


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
    full_name = property_mapping.get('full_name')
    simple_name = full_name.split('.')[-1]
    es_type = property_mapping.get('mapping').get(simple_name).get('type')
    return es_type


def get_simplified_property_aggregatability(property_mapping):
    """
    :param property_mapping: mapping dict from the ES response
    :return: whether the property is aggregatable or not
    """
    es_type = get_es_property_type(property_mapping)
    return es_type in AGGREGATABLE_TYPES
