"""
Module to test the data module
"""
import unittest

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
