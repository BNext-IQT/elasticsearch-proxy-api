# pylint: disable=import-error,unused-argument
"""
Module that tests a group config
"""
from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests getting the configuration of a group
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing getting the configuration of a group')
    print('-------------------------------------------')

    url = f'{server_base_url}/es_data/get_es_document/chembl_molecule/CHEMBL59'
    utils.assert_get_request_succeeds(url)
