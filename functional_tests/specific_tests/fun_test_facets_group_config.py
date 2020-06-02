# pylint: disable=import-error,unused-argument
"""
Module that tests a facets group config
"""
import requests
from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests getting the configuration of a facets group
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing getting the configuration of a facets group')
    print('-------------------------------------------')

    url = f'{server_base_url}/properties_configuration/facets/chembl_activity/browser_facets'
    print('url: ', url)

    config_request = requests.get(url)

    status_code = config_request.status_code
    print(f'status_code: {status_code}')

    response_text = config_request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'
