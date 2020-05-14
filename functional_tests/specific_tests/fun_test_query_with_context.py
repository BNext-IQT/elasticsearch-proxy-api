# pylint: disable=import-error
"""
Module that tests an es_query with context
"""
import json
import time

import requests

from specific_tests import utils


def run_test(server_base_url, delayed_jobs_server_base_path):
    """
    Tests that a simple query to elasticsearch
    :param server_base_url: base url of the running server. E.g. http://127.0.0.1:5000
    :param delayed_jobs_server_base_path: base path for the delayed_jobs
    """

    print('-------------------------------------------')
    print('Testing a es_query with context')
    print('-------------------------------------------')

    job_id = submit_similarity_search_job(delayed_jobs_server_base_path)
    wait_until_job_finished(delayed_jobs_server_base_path, job_id)
    print('Now going to make a request with this context')

    url = utils.get_url_for_get_es_data(server_base_url)
    print('url: ', url)

    es_query = {
        "size": 24,
        "from": 0,
        "query": {
            "bool": {
                "must": [{"query_string": {"analyze_wildcard": 'true', "query": "*"}}],
                "filter": []
            }
        },
        "sort": []
    }

    context_obj = {
        "delayed_jobs_base_url": delayed_jobs_server_base_path,
        "context_type": "SIMILARITY",
        "context_id": "STRUCTURE_SEARCH-V4s_piFIe9FL7sOuJ0jl6U0APMEsoV-b4HfFE_dtojc=",
    }

    payload = {
        'index_name': 'chembl_26_molecule',
        'es_query': json.dumps(es_query),
        'context_obj': json.dumps(context_obj),
        'id_property': 'molecule_chembl_id',
        'contextual_sort_data': {},
    }

    print('payload: ', payload)

    request = requests.post(url, data=payload)

    status_code = request.status_code
    print(f'status_code: {status_code}')
    response_text = request.text
    utils.print_es_response(response_text)
    assert status_code == 200, 'The request failed!'

    response_json = request.json()
    hits = response_json['es_response']['hits']['hits']

    assert len(hits) > 0, 'I should have gotten hits!'

    metadata = response_json['metadata']
    print('metadata: ', metadata)

    assert metadata['total_results'] > 0, 'There should be more than 0 results!'


def submit_similarity_search_job(delayed_jobs_server_base_path):
    """
    :param delayed_jobs_server_base_path: base path of the delayed jobs server
    :return: job_id
    """
    print('Launching a similarity search job...')
    submission_url = utils.get_url_for_similarity_job_submission(delayed_jobs_server_base_path)
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

    status_url = utils.get_url_for_job_status(delayed_jobs_server_base_path, job_id)
    print('status_url: ', status_url)

    status_request = requests.get(status_url)
    print('Status request response code: ', status_request.status_code)

    job_status = None

    while job_status != 'FINISHED':
        status_response = status_request.json()
        job_status = status_response.get('status')
        job_progress = status_response.get('progress')

        print('job_status: ', job_status)
        print('job_progress: ', job_progress)
        time.sleep(1)
