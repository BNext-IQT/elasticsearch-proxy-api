"""
Search parser controller
"""
from flask import Blueprint, jsonify

SEARCH_PARSER_BLUEPRINT = Blueprint('search_parsing', __name__)


@SEARCH_PARSER_BLUEPRINT.route('/parse_free_text_search', methods=['POST'])
def parse_free_text_search():
    """
    :return: the json response with the query to use in elasticsearch
    """

    return jsonify({'parsed_query': 'hola'})
