"""
Service to handle requests asking to get visualisation data
"""
from app.visualisation_data.assay_classification import in_vivo


class VisualisationDataServiceError(Exception):
    """
    Base class for errors in this module
    """


def get_protein_target_classification():
    """
    :return: the protein target classification tree
    """
    return {
        'msg': 'hello'
    }


def get_organism_taxonomy_target_classification():
    """
    :return: the organism taxonomy target classification tree
    """
    return {
        'msg': 'hello'
    }


def get_go_slim_target_classification():
    """
    :return: the go slim target classification tree
    """
    return {
        'msg': 'hello'
    }


def get_in_vivo_assay_classification():
    """
    :return: the in vivo assay classification tree
    """
    return in_vivo.get_classification_tree()
