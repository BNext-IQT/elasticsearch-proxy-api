"""
Module that handles decorators used in http cache
"""
from datetime import datetime, timedelta


def add_cache_headers_to_response(response, hours=24):
    """
    :param response: original flask Response object
    :param hours: the hours for which the content is valid
    :return: the response object with the corresponding cache headers
    """
    expires = datetime.utcnow() + timedelta(hours=hours)
    response.headers.add('Expires', expires.strftime("%a, %d %b %Y %H:%M:%S UTC"))
    response.headers.add('Cache-Control', 'public,max-age=%d' % int(3600 * hours))
