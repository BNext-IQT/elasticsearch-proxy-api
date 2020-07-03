"""
URL Shortening Service
"""
class URLShorteningError(Exception):
    """
    Class for errors in this module
    """

def shorten_url(long_url):
    """
    :param long_url:
    :return: an object with the hash and expiration date of the hash
    """

    return {
        'hash': 'aaa',
        'expires': 'tomorrow'
    }