"""
Service to handle requests asking to get visualisation data
"""
from app.visualisation_data.assay_classification import in_vivo
from app.visualisation_data.target_classification import go_slim
from app.visualisation_data.target_classification import organism_taxonomy
from app.visualisation_data.target_classification import protein_class
from app.cache import CACHE
from app.config import RUN_CONFIG
from app.es_data import es_data


class VisualisationDataServiceError(Exception):
    """
    Base class for errors in this module
    """


def get_protein_target_classification():
    """
    :return: the protein target classification tree
    """
    return protein_class.get_classification_tree()


def get_organism_taxonomy_target_classification():
    """
    :return: the organism taxonomy target classification tree
    """
    return organism_taxonomy.get_classification_tree()


def get_go_slim_target_classification():
    """
    :return: the go slim target classification tree
    """
    return go_slim.get_classification_tree()


def get_in_vivo_assay_classification():
    """
    :return: the in vivo assay classification tree
    """
    return in_vivo.get_classification_tree()


@CACHE.memoize(timeout=RUN_CONFIG.get('es_proxy_cache_seconds'))
def get_database_summary():
    """
    :return: the database_summary
    """

    index_name = 'chembl_document'
    es_query = {
        "_source": False,
        "query": {
            "bool": {
                "filter": {
                    "term": {
                        "doc_type": "DATASET"
                    }
                },
                "must": {
                    "range": {
                        "_metadata.related_activities.count": {
                            "gt": 0
                        }
                    }
                },
                "must_not": {
                    "terms": {
                        "_metadata.source.src_id": [1, 7, 8, 9, 7, 8, 9, 11, 12, 13, 15, 18, 25, 26, 28, 31,
                                                    35, 37, 38,
                                                    39, 41, 42]
                    }
                }
            }
        },
        "track_total_hits": True,
    }

    es_response = es_data.get_es_response(index_name, es_query)

    return {
        'num_datasets': es_response['hits']['total']['value']
    }


# @CACHE.memoize(timeout=RUN_CONFIG.get('es_proxy_cache_seconds'))
def entities_records():
    """
    :return: the database_summary
    """
    drugs_query = {

        "term": {
            "_metadata.drug.is_drug": True
        }

    }

    return {
        'Compounds': get_entity_total_count('chembl_molecule'),
        'Drugs': get_entity_total_count('chembl_molecule', drugs_query),
        'Assays': get_entity_total_count('chembl_assay'),
        'Documents': get_entity_total_count('chembl_document'),
        'Targets': get_entity_total_count('chembl_target'),
        'Cells': get_entity_total_count('chembl_cell_line'),
        'Tissues': get_entity_total_count('chembl_tissue'),
        'Indications': get_entity_total_count('chembl_drug_indication_by_parent'),
        'Mechanisms': get_entity_total_count('chembl_mechanism_by_parent_target')
    }


@CACHE.memoize(timeout=RUN_CONFIG.get('es_proxy_cache_seconds'))
def covid_entities_records():
    """
    :return: the database_summary
    """

    covid_compounds_query = {
        "query_string": {
            "query": "_metadata.compound_records.src_id:52",
        }
    }

    covid_assays_query = {
        "query_string": {
            "query": "_metadata.source.src_id:52",
        }
    }

    covid_documents_query = {
        "query_string": {
            "query": "_metadata.source.src_id:52 AND NOT document_chembl_id:CHEMBL4303081",
        }
    }

    covid_activities_query = {
        "query_string": {
            "query": "_metadata.source.src_id:52",
        }
    }

    return {
        'Compounds': get_entity_total_count('chembl_molecule', query=covid_compounds_query),
        'Assays': get_entity_total_count('chembl_assay', query=covid_assays_query),
        'Documents': get_entity_total_count('chembl_document', query=covid_documents_query),
        'Activities': get_entity_total_count('chembl_activity', query=covid_activities_query),
    }


def get_entity_total_count(index_name, query=None):
    """
    :param index_name: index to query
    :param query: query to apply
    :return: the total count of items of the given entity
    """
    print(f'getting count for index {index_name}')
    total_count_query = {
        "_source": False,
        "track_total_hits": True,
    }
    if query is not None:
        total_count_query['query'] = query

    print('total_count_query: ', total_count_query)

    es_response = es_data.get_es_response(index_name, total_count_query)
    print('es_response: ')
    print(es_response)

    num_items = es_response['hits']['total']['value']

    print(f'num_items: {num_items}')
    print('---')
    return num_items
