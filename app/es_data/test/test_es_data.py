"""
Module to test the data module
"""
import unittest
import json
import hashlib
import base64

from app.es_data import es_data


class TestESData(unittest.TestCase):
    """
    Class to test the es data module
    """

    def test_gets_es_data(self):
        """
        Tests that it returns the es data correctly
        """
        es_query = {
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

        es_index = 'chembl_26_molecule'
        response_got = es_data.get_es_response(es_index, es_query)

        total_hits_must_be = 4
        total_hits_got = response_got['hits']['total']

        self.assertEqual(total_hits_got, total_hits_must_be, msg='The response from elasticsearch was not correct')

    def test_gets_cache_key(self):
        """
        Tests that it generates the correct cache key
        """

        es_query = {
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

        es_index = 'chembl_26_molecule'

        stable_raw_search_data = json.dumps(es_query, sort_keys=True)
        search_data_digest = hashlib.sha256(stable_raw_search_data.encode('utf-8')).digest()
        base64_search_data_hash = base64.b64encode(search_data_digest).decode('utf-8')

        cache_key_must_be = "{}-{}".format(es_index, base64_search_data_hash)
        cache_key_got = es_data.get_es_query_cache_key(es_index, es_query)

        self.assertEqual(cache_key_got, cache_key_must_be, msg='The cache key was not generated correctly!')
