"""
Service to handle requests asking to get visualisation data
"""
from app.visualisation_data.assay_classification import in_vivo
from app.visualisation_data.target_classification import go_slim
from app.visualisation_data.target_classification import organism_taxonomy
from app.visualisation_data.target_classification import protein_class


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


def get_database_summary():
    """
    :return: the database_summary
    """
    return {
        'msg': 'hola'
    }


def entities_records():
    """
    :return: the database_summary
    """
    return {
        'msg': 'hola'
    }


def covid_entities_records():
    """
    :return: the database_summary
    """
    return {
        'msg': 'hola'
    }
