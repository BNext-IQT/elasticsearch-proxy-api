"""
This Module tests the statistics saver
"""
# pylint: disable=R0914
import unittest
import json

from datetime import datetime
from app.config import RUN_CONFIG
from app.usage_statistics import statistics_saver


class TestStatisticsSaver(unittest.TestCase):
    """
    Class to test the statistics saver
    """

    def test_generates_the_correct_json_for_a_cache_record(self):
        """
        Tests that generates the correct json to save a cache record
        """

        full_es_query = {
            'size': 24,
            'from': 0,
            'query': {
                'bool': {
                    'filter': [
                        {
                            'terms': {
                                'molecule_chembl_id': [
                                    'CHEMBL59',
                                    'CHEMBL3247442',
                                    'CHEMBL160074',
                                    'CHEMBL2219748'
                                ]
                            }
                        }
                    ]
                }
            }
        }

        es_index = 'chembl_molecule'
        es_request_digest = 'somedigest'
        is_cached = True
        request_date = datetime.now().timestamp() * 1000
        run_env_type = RUN_CONFIG.get('run_env')
        time_taken = 2.1

        usage_record_dict_got = statistics_saver.get_index_usage_record_dict(es_index, full_es_query, es_request_digest,
                                                                             is_cached, request_date, run_env_type,
                                                                             time_taken)

        es_index_got = usage_record_dict_got.get('es_index')
        self.assertEqual(es_index_got, es_index, msg='The es index was not calculated correctly')

        es_query_got = usage_record_dict_got.get('es_query')
        es_query_must_be = json.dumps(full_es_query.get('query'))
        self.assertEqual(es_query_got, es_query_must_be, msg='The es_query was not calculated correctly')

        es_aggs_got = usage_record_dict_got.get('es_aggs')
        es_aggs_must_be = json.dumps(full_es_query.get('aggs'))
        self.assertEqual(es_aggs_got, es_aggs_must_be, msg='The es_aggs was not calculated correctly')

        es_request_digest_got = usage_record_dict_got.get('es_request_digest')
        self.assertEqual(es_request_digest_got, es_request_digest,
                         msg='The es_request_digest was not calculated correctly')

        is_cached_got = usage_record_dict_got.get('is_cached')
        self.assertEqual(is_cached_got, is_cached,
                         msg='The is_cached was not calculated correctly')

        request_date_got = usage_record_dict_got.get('request_date')
        self.assertEqual(request_date_got, request_date,
                         msg='The request_date was not calculated correctly')

        run_env_type_got = usage_record_dict_got.get('run_env_type')
        self.assertEqual(run_env_type_got, run_env_type,
                         msg='The run_env_type was not calculated correctly')
