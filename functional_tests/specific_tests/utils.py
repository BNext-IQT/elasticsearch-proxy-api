"""
Module with utils functions for the tests
"""
import time

import requests


def get_url_for_get_es_data(server_base_url):
    """
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :return: url for the get_es_data_endpoint
    """
    return f'{server_base_url}/es_data/get_es_data'


def get_url_for_job_status(delayed_jobs_base_url, job_id):
    """
    :param delayed_jobs_base_url: base url for the delayed jobs.
    E.g. https://www.ebi.ac.uk/chembl/interface_api/delayed_jobs
    :param job_id: job_id
    :return: url for getting a job status
    """
    return f'{delayed_jobs_base_url}/status/{job_id}'


def get_url_for_similarity_job_submission(delayed_jobs_base_url):
    """
    :param delayed_jobs_base_url: base url for the delayed jobs.
    E.g. https://www.ebi.ac.uk/chembl/interface_api/delayed_jobs
    :return: url for submitting a similarity search job
    """
    return f'{delayed_jobs_base_url}/submit/structure_search_job'


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


def assert_get_request_succeeds(url_to_test):
    """
    tests that doing a get to the url returns a 200 code
    :param url_to_test: url to test
    """

    print('url: ', url_to_test)

    config_request = requests.get(url_to_test)

    status_code = config_request.status_code
    print(f'status_code: {status_code}')

    response_text = config_request.text
    print_es_response(response_text)
    assert status_code == 200, 'The request failed!'


def submit_similarity_search_job(delayed_jobs_server_base_path):
    """
    :param delayed_jobs_server_base_path: base path of the delayed jobs server
    :return: job_id
    """
    print('Launching a similarity search job...')
    submission_url = get_url_for_similarity_job_submission(delayed_jobs_server_base_path)
    print('submission_url: ', submission_url)

    payload = {
        'search_type': 'SIMILARITY',
        'search_term': 'NCCc1ccc(O)c(O)c1',
        'threshold': 40,
        'dl__ignore_cache': False
    }
    print('payload: ', payload)

    submit_request = requests.post(submission_url, data=payload)
    submission_status_code = submit_request.status_code
    print(f'submission_status_code: {submission_status_code}')
    assert submission_status_code == 200, 'Job could not be submitted!'

    submission_response = submit_request.json()
    job_id = submission_response.get('job_id')
    print('job_id: ', job_id)

    return job_id


def wait_until_job_finished(delayed_jobs_server_base_path, job_id):
    """
    Waits until the job finished
    :param delayed_jobs_server_base_path: base path of the delayed jobs server
    :param job_id: id of the job
    """
    print('Waiting until job finishes...')

    status_url = get_url_for_job_status(delayed_jobs_server_base_path, job_id)
    print('status_url: ', status_url)

    job_status = None

    while job_status != 'FINISHED':
        status_request = requests.get(status_url)
        print('Status request response code: ', status_request.status_code)

        status_response = status_request.json()
        job_status = status_response.get('status')
        job_progress = status_response.get('progress')

        print('job_status: ', job_status)
        print('job_progress: ', job_progress)
        time.sleep(1)
