"""
URL Shortening controller
"""
from flask import Blueprint, jsonify, abort, request

from app.request_validation.decorators import validate_form_with, validate_url_params_with
from app.blueprints.url_shortening.controllers import marshmallow_schemas
from app.blueprints.url_shortening.services import url_shortening_service
from app.http_cache import http_cache_utils

URL_SHORTENING_BLUEPRINT = Blueprint('url_shortening', __name__)


@URL_SHORTENING_BLUEPRINT.route('/shorten_url', methods=['POST'])
@validate_form_with(marshmallow_schemas.ShortenURLRequest)
def shorten_url():
    """
    :return: the json response with the shortened url
    """

    form_data = request.form
    long_url = form_data.get('long_url')

    try:
        shortening_data = url_shortening_service.shorten_url(long_url)
        http_response = jsonify(shortening_data)
        http_cache_utils.add_cache_headers_to_response(http_response)
        return http_response
    except url_shortening_service.URLShorteningError as error:
        abort(500, repr(error))


@URL_SHORTENING_BLUEPRINT.route('/expand_url/<url_hash>', methods=['GET'])
@validate_url_params_with(marshmallow_schemas.ExpandURLRequest)
def expand_url(url_hash):
    """
    :return: the json response with the expanded url
    """

    try:
        expansion_data = url_shortening_service.expand_url(url_hash)
        return jsonify(expansion_data)
    except url_shortening_service.URLShorteningError as error:
        abort(500, repr(error))
    except url_shortening_service.URLNotFoundError as error:
        abort(404, repr(error))
