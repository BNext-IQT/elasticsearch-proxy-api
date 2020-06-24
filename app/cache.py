"""
    Module that handles the connection with the cache
"""
from flask_caching import Cache
import pylibmc

from app.config import RUN_CONFIG
from app import app_logging

CACHE = Cache(config=RUN_CONFIG['cache_config'])


def fail_proof_get(key):
    """
    :param key: the key of the item to get
    :return: the stored item if it extists None if it doesn't or there was a connection failure
    """
    try:
        item = CACHE.get(key=key)
        return item
    # pylint: disable=no-member
    except pylibmc.ConnectionError as error:
        app_logging.error(f"Error while reading from cache({str(error)}). Returning None and continuing. Don't worry")
        return None


def fail_proof_set(key, value, timeout):
    """
    :param key: key to save the item with
    :param value: item to save in the cache
    :param timeout: time for which the item will be valid
    """
    try:
        CACHE.set(key=key, value=value, timeout=timeout)
    # pylint: disable=no-member
    except pylibmc.TooBig as error:
        app_logging.error(f"Error while writing to cache({str(error)}). Continuing. Don't worry")
