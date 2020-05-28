"""
Properties configuration controller
"""
from flask import Blueprint, jsonify, abort, request, send_file

from app.blueprints.properties_config.controllers import marshmallow_schemas
from app.request_validation.decorators import validate_form_with, validate_url_params_with

PROPERTIES_CONFIG_BLUEPRINT = Blueprint('properties_configuration', __name__)

@PROPERTIES_CONFIG_BLUEPRINT.route('/property/<index_name>/<property_id>', methods = ['GET'])
@validate_url_params_with(marshmallow_schemas.PropertyConfigRequest)
def get_property_config(index_name, property_id):

    print('index_name: ', index_name)
    print('property_id: ', property_id)
    return jsonify({'msg': 'hola'})
    # try:
    #     input_file_path = job_status_service.get_input_file_path(job_id, input_key)
    #     return send_file(input_file_path)
    # except job_status_service.InputFileNotFoundError:
    #     abort(404)