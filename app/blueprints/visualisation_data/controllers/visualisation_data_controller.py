"""
Blueprint to handle requests asking to get visualisation data
"""
from flask import Blueprint, abort

from app.blueprints.visualisation_data.services import visualisation_data_service
from app.http_cache import http_cache_utils

VISUALISATION_DATA_BLUEPRINT = Blueprint('visualisation_data', __name__)


@VISUALISATION_DATA_BLUEPRINT.route('/target_classifications/protein_classification', methods=['GET'])
def get_protein_target_classification():
    """
    :return: the json response with the protein target classification
    """
    try:
        json_data = visualisation_data_service.get_protein_target_classification()
        return http_cache_utils.get_json_response_with_http_cache_headers(json_data)
    except visualisation_data_service.VisualisationDataServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')


@VISUALISATION_DATA_BLUEPRINT.route('/target_classifications/organism_taxonomy', methods=['GET'])
def get_organism_taxonomy_target_classification():
    """
    :return: the json response with the organism taxonomy classification
    """
    try:
        json_data = visualisation_data_service.get_organism_taxonomy_target_classification()
        return http_cache_utils.get_json_response_with_http_cache_headers(json_data)
    except visualisation_data_service.VisualisationDataServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')


@VISUALISATION_DATA_BLUEPRINT.route('/target_classifications/go_slim', methods=['GET'])
def get_go_slim_target_classification():
    """
    :return: the json response with the go_slim classification
    """
    try:
        json_data = visualisation_data_service.get_go_slim_target_classification()
        return http_cache_utils.get_json_response_with_http_cache_headers(json_data)
    except visualisation_data_service.VisualisationDataServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')


@VISUALISATION_DATA_BLUEPRINT.route('/assay_classifications/in_vivo', methods=['GET'])
def get_in_vivo_assay_classification():
    """
    :return: the json response with the in vivo assay classification
    """
    try:
        json_data = visualisation_data_service.get_in_vivo_assay_classification()
        return http_cache_utils.get_json_response_with_http_cache_headers(json_data)
    except visualisation_data_service.VisualisationDataServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')


@VISUALISATION_DATA_BLUEPRINT.route('/database_summary', methods=['GET'])
def get_database_summary():
    """
    :return: the json response with the database summary
    """
    try:
        json_data = visualisation_data_service.get_database_summary()
        return http_cache_utils.get_json_response_with_http_cache_headers(json_data)
    except visualisation_data_service.VisualisationDataServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')


@VISUALISATION_DATA_BLUEPRINT.route('/entities_records', methods=['GET'])
def get_entities_records():
    """
    :return: the json response with the entities records
    """
    try:
        json_data = visualisation_data_service.entities_records()
        return http_cache_utils.get_json_response_with_http_cache_headers(json_data)
    except visualisation_data_service.VisualisationDataServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')


@VISUALISATION_DATA_BLUEPRINT.route('/covid_entities_records', methods=['GET'])
def covid_entities_records():
    """
    :return: the json response with the covid entities records
    """
    try:
        json_data = visualisation_data_service.covid_entities_records()
        return http_cache_utils.get_json_response_with_http_cache_headers(json_data)
    except visualisation_data_service.VisualisationDataServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')
