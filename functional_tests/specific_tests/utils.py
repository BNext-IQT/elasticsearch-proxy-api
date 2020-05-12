"""
Module with utils functions for the tests
"""


def get_url_for_get_es_data(server_base_url):
    """
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :return: url for the get_es_data_endpoint
    """
    return f'{server_base_url}/get_es_data'
