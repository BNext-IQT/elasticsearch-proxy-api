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

    def test_gets_config_for_a_group_with_only_default_properties(self):
        """
        tests that gets config for a group with only default properties
        """
        groups_configuration_manager = get_group_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        group_name = 'download'

        configs_got = groups_configuration_manager.get_config_for_group(index_name, group_name)['properties']

        with open(groups_configuration_manager.groups_file_path, 'rt') as groups_config_file:
            groups_must_be = yaml.load(groups_config_file, Loader=yaml.FullLoader)
            group_must_be = groups_must_be[index_name][group_name]

            for sub_group, props_list_must_be in group_must_be.items():
                props_list_got = [conf['prop_id'] for conf in configs_got[sub_group]]
                self.assertTrue(props_list_got == props_list_must_be)

    def test_gets_config_for_a_group_with_default_and_additional_properties(self):
        """
        tests that gets config for a group with default and additional properties
        """
        groups_configuration_manager = get_group_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        group_name = 'table'

        configs_got = groups_configuration_manager.get_config_for_group(index_name, group_name)['properties']

        with open(groups_configuration_manager.groups_file_path, 'rt') as groups_config_file:
            groups_must_be = yaml.load(groups_config_file, Loader=yaml.FullLoader)
            group_must_be = groups_must_be[index_name][group_name]

            for sub_group, props_list_must_be in group_must_be.items():
                props_list_got = [conf['prop_id'] for conf in configs_got[sub_group]]
                self.assertTrue(props_list_got == props_list_must_be)

    def test_gets_all_configured_properties(self):
        """
        Tests that it returns all the configured properties for an index
        """

        groups_configuration_manager = get_group_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'

        props_list_must_be = [
            '_metadata.organism_taxonomy.oc_id', '_metadata.assay_data.assay_subcellular_fraction',
            '_metadata.activity_generated.short_data_validity_comment',
            '_metadata.assay_data.assay_cell_type', '_metadata.assay_data.assay_organism',
            '_metadata.assay_data.assay_tissue'
        ]

        props_list_got = groups_configuration_manager.get_list_of_configured_properties(index_name)

        self.assertEqual(sorted(props_list_got), sorted(props_list_must_be),
                         msg='The properties list is not correct!')
