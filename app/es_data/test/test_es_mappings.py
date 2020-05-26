"""
Module to test the es mappings module
"""
import unittest

from app.config import RUN_CONFIG
from app.es_data import es_mappings


class TestESMappings(unittest.TestCase):
    """
    Class to test the es mappings module
    """

    def test_gets_id_properties_for_index(self):
        """
        Tests it gets id property for index
        """

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}molecule'
        id_properties_must_be = ['molecule_chembl_id']
        print('id_properties_must_be: ', id_properties_must_be)
        id_properties_got = es_mappings.get_id_properties_for_index(index_name)
        print('id_properties_got: ', id_properties_got)

        self.assertEqual(id_properties_must_be, id_properties_got,
                         msg=f'The id property for {index_name} was not returned correctly!')
