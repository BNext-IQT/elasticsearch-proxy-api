"""
Properties configuration controller
"""
from flask import Blueprint, jsonify, abort

from app.blueprints.properties_config.controllers import marshmallow_schemas
from app.request_validation.decorators import validate_url_params_with
from app.blueprints.properties_config.services import properties_config_service
from app.http_cache import http_cache_utils

PROPERTIES_CONFIG_BLUEPRINT = Blueprint('properties_configuration', __name__)


@PROPERTIES_CONFIG_BLUEPRINT.route('/property/<index_name>/<property_id>', methods=['GET'])
@validate_url_params_with(marshmallow_schemas.PropertyConfigRequest)
def get_property_config(index_name, property_id):
    """
    :param index_name: name of the index to which the property belongs
    :param property_id: id of the property to check
    :return: the response for requests asking for property configurations
    """
    try:

        properties_config = properties_config_service.get_property_config(index_name, property_id)
        http_response = jsonify(properties_config)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response

    except properties_config_service.PropertiesConfigServiceError as error:

        abort(500, repr(error))


@PROPERTIES_CONFIG_BLUEPRINT.route('/group/<index_name>/<group_name>', methods=['GET'])
@validate_url_params_with(marshmallow_schemas.GroupConfigRequest)
def get_group_config(index_name, group_name):
    """
    :param index_name: name of the index to which the group belongs
    :param group_name: name of the group to check
    :return: the response for requests asking for group configurations
    """
    try:

        group_config = properties_config_service.get_group_config(index_name, group_name)
        http_response = jsonify(group_config)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response

    except properties_config_service.PropertiesConfigServiceError as error:

        abort(500, repr(error))


@PROPERTIES_CONFIG_BLUEPRINT.route('/facets/<index_name>/<group_name>', methods=['GET'])
@validate_url_params_with(marshmallow_schemas.FacetsGroupConfigRequest)
def get_facet_group_config(index_name, group_name):
    """
    :param index_name: name of the index to which the facet group belongs
    :param group_name: name of the group to check
    :return: the response for requests asking for facet group configurations
    """
    try:

        facet_group_config = properties_config_service.get_facets_group_config(index_name, group_name)
        http_response = jsonify(facet_group_config)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response

    except properties_config_service.PropertiesConfigServiceError as error:

        abort(500, repr(error))


@PROPERTIES_CONFIG_BLUEPRINT.route('/id_properties/<index_name>', methods=['GET'])
@validate_url_params_with(marshmallow_schemas.IDPropertiesRequest)
def get_index_id_properties(index_name):
    """
    :param index_name: name of the index for which to get the id properties
    :return: the response for requests asking for facet group configurations
    """
    try:

        id_properties = properties_config_service.get_index_properties_of_index(index_name)
        http_response = jsonify(id_properties)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response

    except properties_config_service.PropertiesConfigServiceError as error:

        abort(500, repr(error))


@PROPERTIES_CONFIG_BLUEPRINT.route('/all_properties/<index_name>', methods=['GET'])
@validate_url_params_with(marshmallow_schemas.AllPropertiesRequest)
def get_all_configured_properties_for_index(index_name):
    """
    :param index_name: name of the index for which to get the all the properties config
    :return: the json response with the all properties configuration
    """
    try:

        all_properties_configured = properties_config_service.get_all_configured_properties_for_index(index_name)
        http_response = jsonify(all_properties_configured)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response

    except properties_config_service.PropertiesConfigServiceError as error:

        abort(500, repr(error))
