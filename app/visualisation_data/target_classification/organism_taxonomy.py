"""
Module that generates the organism taxonomy target classification
"""

from app import cache
from app import app_logging
from app.visualisation_data.shared.tree_generator import TargetHierarchyTreeGenerator


def get_classification_tree():
    """
    :return: the organism taxonomy target classification tree
    """
    cache_key = 'target_classifications_organism_taxonomy_1'
    app_logging.debug(f'cache_key: {cache_key}')

    cache_response = cache.fail_proof_get(key=cache_key)

    if cache_response is not None:
        app_logging.debug('results are in cache')
        return cache_response

    index_name = 'chembl_organism'
    es_query = {
        "aggs": {
            "children": {
                "terms": {
                    "field": "l1",
                    "size": 100,
                    "order": {
                        "_count": "desc"
                    }
                },
                "aggs": {
                    "children": {
                        "terms": {
                            "field": "l2",
                            "size": 100,
                            "order": {
                                "_count": "desc"
                            }
                        },
                        "aggs": {
                            "children": {
                                "terms": {
                                    "field": "l3",
                                    "size": 100,
                                    "order": {
                                        "_count": "desc"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    def generate_count_query(path_to_node):

        queries = []
        level = 1
        for node in path_to_node:
            queries.append('_metadata.organism_taxonomy.l{level}:("{class_name}")'.format(level=level, class_name=node))
            level += 1

        return ' AND '.join(queries)

    tree_generator = TargetHierarchyTreeGenerator(index_name=index_name, es_query=es_query,
                                                  query_generator=generate_count_query,
                                                  count_index='chembl_target')

    final_tree = tree_generator.get_classification_tree()

    cache_time = int(3.154e7)
    cache.fail_proof_set(key=cache_key, value=final_tree, timeout=cache_time)

    return final_tree
