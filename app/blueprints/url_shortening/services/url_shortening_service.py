"""
URL Shortening Service
"""
from app.url_shortening import url_shortener


class URLShorteningError(Exception):
    """
    Class for errors in this module
    """


def shorten_url(long_url):
    """
    :param long_url:
    :return: an object with the hash and expiration date of the hash
    """

    sortened_url_dict = url_shortener.shorten_url(long_url)

    return sortened_url_dict
