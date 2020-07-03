"""
URL Shortening controller
"""
from flask import Blueprint, jsonify, abort, request

URL_SHORTENING_BLUEPRINT = Blueprint('url_shortening', __name__)

@URL_SHORTENING_BLUEPRINT.route('/shorten_url', methods=['POST'])
def shorten_url():
    """
    :return: the json response with the shortened url
    """
    return jsonify({'msg': 'hola'})