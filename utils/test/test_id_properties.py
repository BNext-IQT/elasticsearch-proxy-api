"""
Module to test the id_properties module
"""
import unittest

from utils import id_properties


class TestIDProperties(unittest.TestCase):
    """
    Class to test the id_properties module
    """

    def test_gets_id_property_value_for_single_id_property(self):
        """
        Tests that given a list of id properties with a single property returns the correct id value
        """

        item = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        id_properties_list = ['a']

        id_value_got = id_properties.get_id_value(id_properties_list, item)
        id_value_must_be = str(item['a'])

        self.assertEqual(id_value_got, id_value_must_be, msg='The id value was not calculated correctly!')

    def test_gets_id_property_value_for_multiple_id_properties(self):
        """
        Tests that given a list of id properties with multiple properties returns the correct id value
        """

        item = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        id_properties_list = ['a', 'b']

        id_value_got = id_properties.get_id_value(id_properties_list, item)
        id_value_must_be = f'{str(item["a"])}-{str(item["b"])}'

        self.assertEqual(id_value_got, id_value_must_be, msg='The id value was not calculated correctly!')

    def test_gets_id_property_value_for_multiple_id_properties_when_one_value_is_none(self):
        """
        Tests that given a list of id properties with multiple properties returns the correct id value
        """

        item = {
            'a': 1,
            'b': None,
            'c': 3
        }

        id_properties_list = ['a', 'b']

        id_value_got = id_properties.get_id_value(id_properties_list, item)
        id_value_must_be = f'{str(item["a"])}-None'

        self.assertEqual(id_value_got, id_value_must_be, msg='The id value was not calculated correctly!')
