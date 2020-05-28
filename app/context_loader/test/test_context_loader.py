"""
Module to test the context loader
"""
import unittest
import re

from app.context_loader import context_loader
from app.config import RUN_CONFIG


class TestContextLoader(unittest.TestCase):
    """
    Class to test the functions used in the context loader
    """

    def test_generates_the_correct_context_url(self):
        """
        Tests that generates the initial url to load a context
        """
        context_dict = {
            'delayed_jobs_base_url': 'https://www.ebi.ac.uk/chembl/interface_api/delayed_jobs',
            'context_type': 'SIMILARITY',
            'context_id': 'STRUCTURE_SEARCH-V4s_piFIe9FL7sOuJ0jl6U0APMEsoV-b4HfFE_dtojc='
        }

        host = re.search(r'[^/]+\.ebi\.ac\.uk(:\d+)?', context_dict["delayed_jobs_base_url"]).group(0)
        host_mappings = RUN_CONFIG.get('delayed_jobs', {}).get('server_mapping', {})
        mapped_host = host_mappings.get(host)
        mapped_base_url = context_dict['delayed_jobs_base_url'].replace(host, mapped_host)
        base_url_with_correct_schema = mapped_base_url.replace('https://', 'http://')

        context_url_must_be = f'{base_url_with_correct_schema}/outputs/{context_dict["context_id"]}/results.json'

        context_url_got = context_loader.get_context_url(context_dict)
        self.assertEqual(context_url_must_be, context_url_got, msg='The context url was not generated correctly!')
