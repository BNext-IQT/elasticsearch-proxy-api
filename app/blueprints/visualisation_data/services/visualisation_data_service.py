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


@CACHE.memoize(timeout=RUN_CONFIG.get('es_proxy_cache_seconds'))
def entities_records():
    """
    :return: the database_summary
    """
    return {
        'msg': 'hola'
    }


@CACHE.memoize(timeout=RUN_CONFIG.get('es_proxy_cache_seconds'))
def covid_entities_records():
    """
    :return: the database_summary
    """
    return {
        'msg': 'hola'
    }
