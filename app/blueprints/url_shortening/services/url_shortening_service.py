"""
URL Shortening Service
"""
from app.url_shortening import url_shortener


class URLShorteningError(Exception):
    """
    Class for errors in this module
    """

class URLNotFoundError(Exception):
    """
    Class for errors when an url is not found
    """


def shorten_url(long_url):
    """
    :param long_url:
    :return: an object with the hash and expiration date of the hash
    """

    sortened_url_dict = url_shortener.shorten_url(long_url)

    return sortened_url_dict


def expand_url(url_hash):
    """
    :param url_hash: hash of the url to expand
    :return: an object with the expanded url and expiration date of the hash
    """
    print('expand_url service: ', url_hash)
    try:
        expanded_url_dict = url_shortener.expand_url(url_hash)
        return expanded_url_dict
    except url_shortener.URLNotFoundError as error:
        raise URLNotFoundError(str(error))
