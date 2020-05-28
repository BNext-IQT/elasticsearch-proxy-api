"""
Properties configuration controller
"""
from flask import Blueprint, jsonify, abort

from app.blueprints.properties_config.controllers import marshmallow_schemas
from app.request_validation.decorators import validate_url_params_with
from app.blueprints.properties_config.services import properties_config_service

PROPERTIES_CONFIG_BLUEPRINT = Blueprint('properties_configuration', __name__)

@PROPERTIES_CONFIG_BLUEPRINT.route('/property/<index_name>/<property_id>', methods = ['GET'])
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