"""
Element usage controller
"""
from flask import Blueprint, jsonify, abort, request

from app.request_validation.decorators import validate_form_with
from app.blueprints.element_usage_blueprint.controllers import marshmallow_schemas
from app.blueprints.element_usage_blueprint.services import element_usage_service

ELEMENT_USAGE_BLUEPRINT = Blueprint('frontend_element_usage', __name__)


@ELEMENT_USAGE_BLUEPRINT.route('/register_element_usage', methods=['POST'])
@validate_form_with(marshmallow_schemas.RegisterUsageRequest)
def register_element_usage():
    """
    :return: the json response with the operation result
    """

    form_data = request.form
    view_name = form_data.get('view_name')
    view_type = form_data.get('view_type')
    entity_name = form_data.get('entity_name')

    try:
        operation_result = element_usage_service.register_element_usage(view_name, view_type, entity_name)
        return jsonify(operation_result)
    except element_usage_service.UsageRegistrationError as error:
        abort(500, repr(error))
