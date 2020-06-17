# pylint: disable=import-error
"""
Module that tests getting a context data
"""
import requests

from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests that getting the data of a context
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing getting the data of a context')
    print('-------------------------------------------')

    job_id = utils.submit_similarity_search_job(delayed_jobs_server_base_path)
    utils.wait_until_job_finished(delayed_jobs_server_base_path, job_id)
    print('Now going to load this context')

    context_params = {
        'delayed_jobs_base_url': 'https://www.ebi.ac.uk/chembl/interface_api/delayed_jobs',
        'context_type': 'SIMILARITY',
        'context_id': f'{job_id}'
    }

    url = f'{server_base_url}/contexts/get_context_data'

    request = requests.post(url, data=context_params)

    status_code = request.status_code
    print(f'status_code: {status_code}')
    response_text = request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'
