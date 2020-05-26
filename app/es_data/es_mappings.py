"""
Module that returns mapping data from elascticsearch
"""
from app.es_connection import ES
from app import app_logging
from app.es_data import utils
from utils import dict_property_access
from app.config import RUN_CONFIG
from app.cache import CACHE

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

ES_INDEX_PREFIX = RUN_CONFIG.get("es_index_prefix")

ID_PROPERTIES = {
    f'{ES_INDEX_PREFIX}activity': ['activity_id'],
    f'{ES_INDEX_PREFIX}activity_supplementary_data_by_activity': ['activity_id'],
    f'{ES_INDEX_PREFIX}assay': ['assay_chembl_id'],
    f'{ES_INDEX_PREFIX}assay_class': ['assay_class_id'],
    f'{ES_INDEX_PREFIX}atc_class': ['level5'],
    f'{ES_INDEX_PREFIX}binding_site': ['site_id'],
    f'{ES_INDEX_PREFIX}biotherapeutic': ['molecule_chembl_id'],
    f'{ES_INDEX_PREFIX}cell_line': ['cell_chembl_id'],
    f'{ES_INDEX_PREFIX}chembl_id_lookup': ['chembl_id'],
    f'{ES_INDEX_PREFIX}compound_record': ['record_id'],
    f'{ES_INDEX_PREFIX}document': ['document_chembl_id'],
    f'{ES_INDEX_PREFIX}document_similarity': ['document_1_chembl_id', 'document_2_chembl_id',
                                              'mol_tani', 'tid_tani'],
    f'{ES_INDEX_PREFIX}drug': ['molecule_chembl_id'],
    f'{ES_INDEX_PREFIX}mechanism': ['mec_id'],
    f'{ES_INDEX_PREFIX}molecule': ['molecule_chembl_id'],
    f'{ES_INDEX_PREFIX}molecule_form': ['molecule_chembl_id'],
    f'{ES_INDEX_PREFIX}organism': ['tax_id'],
    f'{ES_INDEX_PREFIX}protein_class': ['protein_class_id'],
    f'{ES_INDEX_PREFIX}source': ['src_id'],
    f'{ES_INDEX_PREFIX}target': ['target_chembl_id'],
    f'{ES_INDEX_PREFIX}target_component': ['component_id'],
    f'{ES_INDEX_PREFIX}target_relation': ['target_chembl_id', 'related_target_chembl_id'],
    f'{ES_INDEX_PREFIX}tissue': ['tissue_chembl_id'],
    f'{ES_INDEX_PREFIX}metabolism': ['met_id'],
    f'{ES_INDEX_PREFIX}drug_indication': ['drugind_id'],
    f'{ES_INDEX_PREFIX}go_slim': ['go_id']

}


class EsMappingsError(Exception):
    """Base class for exceptions in the ES Mappings"""


@CACHE.memoize(timeout=RUN_CONFIG.get('es_mappings_cache_seconds'))
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


@CACHE.memoize(timeout=RUN_CONFIG.get('es_mappings_cache_seconds'))
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


def get_id_properties_for_index(index_name):
    """
    :param index_name: name of the index
    :return: the id properties for an index
    """
    id_properties = ID_PROPERTIES.get(index_name)
    if id_properties is None:
        EsMappingsError(f'The index {index_name} does not exist or does not have an id property defined')
    return id_properties
