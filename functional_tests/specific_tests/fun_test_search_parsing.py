# pylint: disable=import-error,unused-argument
"""
Module that tests parsing a search term
"""
import requests

from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests that parsing a search term works
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing parsing s search')
    print('-------------------------------------------')

    term_params = {
        'search_term': 'MDCK',
        'es_indexes': 'chembl_molecule,chembl_target,chembl_assay,chembl_document,chembl_cell_line,chembl_tissue',
    }

    url = f'{server_base_url}/search_parsing/parse_free_text_search'

    request = requests.post(url, data=term_params)

    status_code = request.status_code
    print(f'status_code: {status_code}')
    response_text = request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'
