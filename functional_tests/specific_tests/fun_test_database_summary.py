# pylint: disable=import-error,unused-argument
"""
Module that tests a the database summary
"""
from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests getting the go slim target classification
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing getting the database summary')
    print('-------------------------------------------')

    url = f'{server_base_url}/visualisations/database_summary'
    utils.assert_get_request_succeeds(url)
