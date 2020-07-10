# pylint: disable=import-error,unused-argument
"""
Module that tests a the covid entities records
"""
from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests getting the protein target classification
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing getting the covid entities_records')
    print('-------------------------------------------')

    url = f'{server_base_url}/visualisations/covid_entities_records'
    utils.assert_get_request_succeeds(url)
