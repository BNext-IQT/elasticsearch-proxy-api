# pylint: disable=import-error
"""
Module that tests the element usage endpoint
"""
import requests

from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests an the element usage query to elasticsearch
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing the element usage endpoint')
    print('-------------------------------------------')
    print('delayed_jobs_server_base_path: ', delayed_jobs_server_base_path)

    url = f'{server_base_url}/es_data/frontend_element_usage/register_element_usage'

    payload = {
        'view_name': 'Compound-CompoundNameAndClassification',
        'view_type': 'CARD',
        'entity_name': 'Compound'
    }

    request = requests.post(url, data=payload)

    status_code = request.status_code
    print(f'status_code: {status_code}')
    response_text = request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'
