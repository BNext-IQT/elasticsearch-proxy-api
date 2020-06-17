"""
Contexts controller
"""
from flask import Blueprint, jsonify, abort, request

from app.request_validation.decorators import validate_form_with
from app.blueprints.contexts.controllers import marshmallow_schemas
from app.blueprints.contexts.services import contexts_service


CONTEXTS_BLUEPRINT = Blueprint('contexts', __name__)

@CONTEXTS_BLUEPRINT.route('/get_context_data', methods=['POST'])
@validate_form_with(marshmallow_schemas.ContextDataRequest)
def get_context_data():
    """
    :return: the json response with the context data
    """

    form_data = request.form

    context_type = form_data.get('context_type')
    context_id = form_data.get('context_id')
    delayed_jobs_base_url = form_data.get('delayed_jobs_base_url')

    context_dict = {
        'context_type': context_type,
        'context_id': context_id,
        'delayed_jobs_base_url': delayed_jobs_base_url
    }

    try:
        context_data = contexts_service.get_context_data(context_dict)
        return jsonify(context_data)
    except contexts_service.ContextError as error:
        abort(500, repr(error))