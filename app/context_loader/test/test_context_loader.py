"""
Module to test the context loader
"""
import unittest

from app.config import RUN_CONFIG
from app.context_loader import context_loader


class TestContextLoader(unittest.TestCase):
    """
    Class to test the functions used in the context loader
    """

    def test_generates_the_correct_context_url(self):
        """
        Tests that generates the initial url to load a context
        """
        context_dict = {
            'context_type': 'SIMILARITY',
            'context_id': 'STRUCTURE_SEARCH-V4s_piFIe9FL7sOuJ0jl6U0APMEsoV-b4HfFE_dtojc='
        }

        delayed_jobs_config = RUN_CONFIG.get('delayed_jobs')
        delayed_jobs_base_url = delayed_jobs_config.get('base_url')

        context_url_must_be = f'{delayed_jobs_base_url}/outputs/{context_dict["context_id"]}/results.json'

        print('context_url_must_be: ', context_url_must_be)

        context_url_got = context_loader.get_context_url(context_dict)

        self.assertEqual(context_url_must_be, context_url_got, msg='The context url was not generated correctly!')
