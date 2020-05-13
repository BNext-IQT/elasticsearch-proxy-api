"""
Module with utils functions for the tests
"""


def get_url_for_get_es_data(server_base_url):
    """
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :return: url for the get_es_data_endpoint
    """
    return f'{server_base_url}/es_data/get_es_data'


def print_es_response(response_text, max_chars=200):
    """
    prints the response text passed as parameter up to max_chars
    :param response_text: response to print
    :param max_chars: max chars to print
    """
    print('response_text:')

    too_long = len(response_text) > max_chars

    if too_long:
        print(f'{response_text[0:max_chars]}...')
    else:
        print(response_text)
