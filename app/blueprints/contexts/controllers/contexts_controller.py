"""
Contexts controller
"""
from flask import Blueprint, jsonify, abort

from app.blueprints.contexts.controllers import marshmallow_schemas
from app.request_validation.decorators import validate_form_with
from app.blueprints.contexts.controllers import marshmallow_schemas


CONTEXTS_BLUEPRINT = Blueprint('contexts', __name__)

@CONTEXTS_BLUEPRINT.route('/get_context_data', methods=['POST'])
@validate_form_with(marshmallow_schemas.ContextDataRequest)
def get_context_data():
    """
    :return: the json response with the context data
    """
    return jsonify({'msg': 'hola'})