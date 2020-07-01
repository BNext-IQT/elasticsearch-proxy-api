"""
Search Parsing Service
"""
import time

from app.free_text_parsing import free_text_parser
from app.usage_statistics import statistics_saver


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
    start_time = time.time()
    response_dict = free_text_parser.parse_search(search_term, es_indexes, selected_es_index)
    end_time = time.time()
    time_taken = end_time - start_time

    statistics_saver.save_free_text_search_record(time_taken)

    return response_dict
