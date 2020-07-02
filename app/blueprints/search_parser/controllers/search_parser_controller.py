"""
Search parser controller
"""
from flask import Blueprint, jsonify, abort, request

from app.request_validation.decorators import validate_form_with
from app.blueprints.search_parser.controllers import marshmallow_schemas
from app.blueprints.search_parser.services import search_parsing_service
from app.http_cache import http_cache_utils

SEARCH_PARSER_BLUEPRINT = Blueprint('search_parsing', __name__)


@SEARCH_PARSER_BLUEPRINT.route('/parse_free_text_search', methods=['POST'])
@validate_form_with(marshmallow_schemas.ParseFreeTextSearchRequest)
def parse_free_text_search():
    """
    :return: the json response with the query to use in elasticsearch
    """

    form_data = request.form

    search_term = form_data.get('search_term')
    es_indexes = form_data.get('es_indexes')
    selected_es_index = form_data.get('selected_es_index')

    try:
        raw_response = search_parsing_service.parse_search(search_term, es_indexes, selected_es_index)
        http_response = jsonify(raw_response)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response
    except search_parsing_service.SearchParsingServiceError as error:
        abort(500, repr(error))
