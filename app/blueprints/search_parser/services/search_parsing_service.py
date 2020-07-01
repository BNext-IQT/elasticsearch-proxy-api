"""
Search Parsing Service
"""
from app.free_text_parsing import free_text_parser


class SearchParsingServiceError(Exception):
    """
    Class for errors in this module
    """


def parse_search(search_term, es_indexes, selected_es_index):
    """
    :param search_term: Term to parse
    :param es_indexes: indexes in which the search will be done, separated by a comma
    :param selected_es_index: es index to focus on
    :return: the query to send to elasticsearch based on the search term provided
    """
    parsed_query = free_text_parser.parse_search(search_term, es_indexes, selected_es_index)
    return {'parsed_query': parsed_query}
