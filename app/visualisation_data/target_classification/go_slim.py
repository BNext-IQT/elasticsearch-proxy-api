"""
Module that generates the go slim target classification
"""

from app import cache
from app import app_logging
from app.visualisation_data.shared.tree_generator import GoSlimTreeGenerator


def get_classification_tree():
    """
    :return: the go slim target classification tree
    """

    cache_key = 'target_classifications_go_slim_1'
    app_logging.debug(f'cache_key: {cache_key}')

    cache_response = cache.fail_proof_get(key=cache_key)

    if cache_response is not None:
        app_logging.debug('results are in cache')
        return cache_response

    tree_generator = GoSlimTreeGenerator()
    final_tree = tree_generator.get_classification_tree()


    cache_time = int(3.154e7)
    cache.fail_proof_set(key=cache_key, value=final_tree, timeout=cache_time)

    return final_tree
