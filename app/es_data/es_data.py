"""
Module that returns data from elascticsearch
"""
from app.es_connection import ES


def get_es_response(index_name, search_data):
    """""
    :param index_name: name of the index to query against
    :param search_data: dict with the query to send
    """

    response = ES.search(index=index_name, body=search_data)
    return response
