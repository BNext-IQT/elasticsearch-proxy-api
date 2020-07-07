# pylint: disable=import-error, unused-import
"""
Module that tests a url shortening
"""
import json

import requests

from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests that a url can be shortened
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing the url shortening')
    print('-------------------------------------------')
    print('delayed_jobs_server_base_path: ', delayed_jobs_server_base_path)

    url = f'{server_base_url}/url_shortening/shorten_url'
    print('url: ', url)
    long_url = '#substructure_search_results/C[C@H](CCc1ccccc1)NC[C@H](O)c1ccc(O)c(C(N)=O)c1'

    payload = {
        "long_url": long_url
    }

    request = requests.post(url, data=payload)

    status_code = request.status_code
    print(f'status_code: {status_code}')
    response_text = request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'

    response_json = request.json()
    url_hash = response_json.get('hash')
    assert url_hash is not None, 'The url hash was not returned!'

    expansion_url = f'{server_base_url}/url_shortening/expand_url/{url_hash}'
    request = requests.get(expansion_url)

    status_code = request.status_code
    print(f'status_code: {status_code}')
    response_text = request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'

    response_json = request.json()
    long_url_got = response_json.get('long_url')
    assert long_url == long_url_got, 'The long url was not obtained!'
