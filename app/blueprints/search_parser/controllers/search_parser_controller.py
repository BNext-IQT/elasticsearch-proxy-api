"""
Search parser controller
"""
from flask import Blueprint, jsonify

from app.request_validation.decorators import validate_form_with
from app.blueprints.search_parser.controllers import marshmallow_schemas

SEARCH_PARSER_BLUEPRINT = Blueprint('search_parsing', __name__)


@SEARCH_PARSER_BLUEPRINT.route('/parse_free_text_search', methods=['POST'])
@validate_form_with(marshmallow_schemas.ParseFreeTextSearchRequest)
def parse_free_text_search():
    """
    :return: the json response with the query to use in elasticsearch
    """

    return jsonify({'parsed_query': 'hola'})
