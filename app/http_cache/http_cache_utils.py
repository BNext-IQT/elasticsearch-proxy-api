"""
Module that handles decorators used in http cache
"""
from datetime import datetime, timedelta

from flask import jsonify


def add_cache_headers_to_response(response, hours=24):
    """
    :param response: original flask Response object
    :param hours: the hours for which the content is valid
    :return: the response object with the corresponding cache headers
    """
    expires = datetime.utcnow() + timedelta(hours=hours)
    response.headers.add('Expires', expires.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    response.headers.add('Cache-Control', 'public,max-age=%d' % int(3600 * hours))
    response.add_etag()

def get_json_response_with_http_cache_headers(json_data):
    """
    :param json_data: data to include in the response
    :return: json_response with the data and headers included
    """

    http_response = jsonify(json_data)
    add_cache_headers_to_response(http_response)
    return http_response
