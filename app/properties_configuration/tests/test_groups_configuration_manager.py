"""
Module to test groups configuration manager
"""
import unittest

import yaml

from app.properties_configuration.tests import test_property_configuration_manager
from app.properties_configuration.groups_configuration_manager import GroupConfiguration
from app.properties_configuration.properties_configuration_manager import PropertyConfiguration
from app.config import RUN_CONFIG

def get_group_configuration_instance():
    """
    :return: a test instance of the configuration manager
    """
    configuration_manager = test_property_configuration_manager.get_property_configuration_instance()

    group_configuration_manager = GroupConfiguration(
        groups_file_path='app/properties_configuration/tests/data/test_groups.yml',
        sorting_file_path='app/properties_configuration/tests/data/test_default_sorting.yml',
        property_configuration_manager=configuration_manager
    )

    return group_configuration_manager

class GroupsConfigurationManagerTester(unittest.TestCase):
    """
    Class to test the configuration manager
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Getting a custom list of properties
    # ------------------------------------------------------------------------------------------------------------------
    def test_fails_config_for_a_list_of_properties_when_index_does_not_exist(self):
        """
        test it fails to get config for a list of properties when index does not exist
        """
        groups_configuration_manager = get_group_configuration_instance()

        index_name = 'does_not_exist'
        props = ['_metadata.assay_data.assay_subcellular_fraction']

        with self.assertRaises(PropertyConfiguration.PropertiesConfigurationManagerError,
                               msg='This should have thrown an exception for a non existing index!'):
            groups_configuration_manager.get_config_for_props_list(index_name, props)

    def test_fails_config_for_a_list_of_properties_when_property_does_not_exist(self):
        """
        test it fails to get config for a list of properties when a property does not exist
        """
        groups_configuration_manager = get_group_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        props = ['does_not_exist']

        with self.assertRaises(PropertyConfiguration.PropertiesConfigurationManagerError,
                               msg='This should have thrown an exception for a non existing property!'):
            groups_configuration_manager.get_config_for_props_list(index_name, props)

    def test_gets_config_for_a_list_of_properties(self):
        """
        Test it gets the configuration for a list of properties
        """
        groups_configuration_manager = get_group_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        props = ['_metadata.activity_generated.short_data_validity_comment', '_metadata.assay_data.assay_cell_type']

        configs_got = groups_configuration_manager.get_config_for_props_list(index_name, props)
        config = configs_got[0]
        self.assertEqual(config['index_name'], index_name)
        self.assertEqual(config['prop_id'], props[0])
        self.assertTrue(config['aggregatable'])
        self.assertEqual(config['type'], 'string')
        self.assertEqual(config['label'], 'My custom label')
        self.assertEqual(config['label_mini'], 'My cstm lbl')

        config = configs_got[1]
        self.assertEqual(config['index_name'], index_name)
        self.assertEqual(config['prop_id'], props[1])
        self.assertTrue(config['aggregatable'])
        self.assertEqual(config['type'], 'string')
        self.assertEqual(config['label'], 'Assay Data Cell Type')
        self.assertEqual(config['label_mini'], 'Assay Data Cell Type')

    # ------------------------------------------------------------------------------------------------------------------
    # Getting a group of properties
    # ------------------------------------------------------------------------------------------------------------------
    def test_gets_config_for_a_group_fails_when_index_does_not_exist(self):
        """
        tests that getting config for a group fails when index does not exist
        """

        index_name = 'does_not_exist'
        group_name = 'download'

        groups_configuration_manager = get_group_configuration_instance()

        with self.assertRaises(GroupConfiguration.GroupsConfigurationManagerError,
                               msg='This should have thrown an exception for a non existing property!'):
            groups_configuration_manager.get_config_for_group(index_name, group_name)

    def test_gets_config_for_a_group_fails_when_group_does_not_exist(self):
        """
        tests that gets_config_for_a_group fails when group does not exist
        """

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        group_name = 'does_not_exist'

        groups_configuration_manager = get_group_configuration_instance()
        with self.assertRaises(GroupConfiguration.GroupsConfigurationManagerError,
                               msg='This should have thrown an exception for a non existing property!'):
            groups_configuration_manager.get_config_for_group(index_name, group_name)
