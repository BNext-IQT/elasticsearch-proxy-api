# pylint: disable=import-error
"""
Module that tests a simple es query
"""
import json

import requests

from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests that a simple query to elasticsearch
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing a simple query')
    print('-------------------------------------------')

    url = utils.get_url_for_get_es_data(server_base_url)
    print('url: ', url)
    index_name = 'chembl_26_molecule'
    print('index_name: ', index_name)
    es_query = {
        "size": 24,
        "from": 0,
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"analyze_wildcard": True, "query": "*"}}
                ],
                "filter": []
            }
        },
        "sort": []
    }
    print('es_query: ', es_query)

    payload = {
        'index_name': index_name,
        'es_query': json.dumps(es_query)
    }

    request = requests.post(url, data=payload)

    status_code = request.status_code
    print(f'status_code: {status_code}')
    response_text = request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'

    response_json = request.json()
    hits = response_json['es_response']['hits']['hits']

    assert len(hits) > 0, 'I should have gotten hits!'
