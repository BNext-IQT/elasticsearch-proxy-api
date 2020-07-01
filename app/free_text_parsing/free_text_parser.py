"""
Entry module for the free text parsing package
"""
import re

import arpeggio

from app.free_text_parsing.parser import PARSER
from app.free_text_parsing.query_builder.query_builder import QueryBuilder
from app.free_text_parsing.terms_visitor import TERMS_VISITOR


def parse_query_str(query_string: str):
    """
    :param query_string: the text term to parse
    :return: the es query to apply to es
    """
    if len(query_string.strip()) == 0:
        return {}
    query_string = re.sub(r'[\s&&[^\n]]+', ' ', query_string)
    parse_tree = PARSER.parse(query_string)
    result = arpeggio.visit_parse_tree(parse_tree, TERMS_VISITOR)
    return result


def parse_search(search_term, es_indexes, selected_es_index):
    """
    :param search_term: Term to parse
    :param es_indexes: indexes in which the search will be done, separated by a comma
    :param selected_es_index: es index to focus on
    :return: the query to send to elasticsearch based on the search term provided
    """

    parsed_query = parse_query_str(search_term)

    indexes_list = es_indexes.split(',')
    best_queries, sorted_indexes_by_score = QueryBuilder.get_best_es_query(parsed_query, indexes_list, selected_es_index)

    response_dict = {
        'parsed_query': parsed_query,
        'best_es_base_queries': best_queries,
        'sorted_indexes_by_score': sorted_indexes_by_score
    }

    return response_dict
