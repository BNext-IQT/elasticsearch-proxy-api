"""
Entry module for the free text parsing package
"""


def parse_search(search_term, es_indexes, selected_es_index):
    """
    :param search_term: Term to parse
    :param es_indexes: indexes in which the search will be done, separated by a comma
    :param selected_es_index: es index to focus on
    :return: the query to send to elasticsearch based on the search term provided
    """

    response_dict = {
        'parsed_query': {},
        'best_es_base_queries': {},
        'sorted_indexes_by_score': {}
    }

    return response_dict
