"""
URL Shortening controller
"""
from flask import Blueprint, jsonify, abort, request

from app.request_validation.decorators import validate_form_with
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
