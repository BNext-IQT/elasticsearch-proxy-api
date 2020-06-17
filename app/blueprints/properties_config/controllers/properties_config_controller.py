"""
Properties configuration controller
"""
from flask import Blueprint, jsonify, abort

from app.blueprints.properties_config.controllers import marshmallow_schemas
from app.request_validation.decorators import validate_url_params_with
from app.blueprints.properties_config.services import properties_config_service

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
        return jsonify(properties_config)

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
        return jsonify(group_config)

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
        return jsonify(facet_group_config)

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
        return jsonify(id_properties)

    except properties_config_service.PropertiesConfigServiceError as error:

        abort(500, repr(error))
