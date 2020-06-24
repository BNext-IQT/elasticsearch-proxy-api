"""
    The blueprint used for handling requests to get generic es_data
"""
from flask import Blueprint, jsonify, abort, request

from app.request_validation.decorators import validate_form_with, validate_url_params_with
from app.blueprints.es_proxy.controllers import marshmallow_schemas
from app.blueprints.es_proxy.services import es_proxy_service
from app import app_logging
from app.http_cache import http_cache_utils


ES_PROXY_BLUEPRINT = Blueprint('es_proxy', __name__)


@ES_PROXY_BLUEPRINT.route('/get_es_data', methods=['POST'])
@validate_form_with(marshmallow_schemas.ESProxyQuery)
def get_es_data():
    """
    :return: the json response with the data from elasticsearch
    """
    form_data = request.form

    index_name = sanitise_parameter(form_data.get('index_name'))
    raw_es_query = sanitise_parameter(form_data.get('es_query'))
    raw_context = sanitise_parameter(form_data.get('context_obj'))
    raw_contextual_sort_data = sanitise_parameter(form_data.get('contextual_sort_data'))

    app_logging.debug(f'index_name: {index_name}')
    app_logging.debug(f'raw_es_query: {raw_es_query}')
    app_logging.debug(f'raw_context: {raw_context}')
    app_logging.debug(f'raw_contextual_sort_data: {raw_contextual_sort_data}')

    try:

        json_response = es_proxy_service.get_es_data(
            index_name,
            raw_es_query,
            raw_context,
            raw_contextual_sort_data)

        http_response = jsonify(json_response)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response

    except es_proxy_service.ESProxyServiceError as error:

        abort(500, msg=f'Internal server error: {str(error)}')


@ES_PROXY_BLUEPRINT.route('/get_es_document/<index_name>/<doc_id>', methods=['GET'])
@validate_url_params_with(marshmallow_schemas.ESProxyDoc)
def get_es_doc(index_name, doc_id):
    """
    :param index_name: name of the index to which the doc belongs
    :param doc_id: id of the document to search for
    :return: the json response with the es_doc data
    """
    try:
        json_response = es_proxy_service.get_es_doc(index_name, doc_id)
        http_response = jsonify(json_response)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response
    except es_proxy_service.ESProxyServiceError as error:
        abort(500, msg=f'Internal server error: {str(error)}')
    except es_proxy_service.ESDataNotFoundError as error:
        abort(404)


def sanitise_parameter(param_value):
    """
    Makes the parameter null if it is 'null' or 'undefined', in some cases javascript produces those values
    :param param_value: value of the parameter
    :return: null if param_value in ('null', 'undefined'), the actual value otherwise
    """
    if param_value in ('null', 'undefined'):
        return None
    return param_value
