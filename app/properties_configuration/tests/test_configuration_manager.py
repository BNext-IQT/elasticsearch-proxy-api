"""
Module to test configuration manager
"""
import unittest

import yaml

from app.properties_configuration.properties_configuration_manager import PropertyConfiguration
from app.properties_configuration.groups_configuration_manager import GroupConfiguration
from app.config import RUN_CONFIG


# ------------------------------------------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------------------------------------------
def get_property_configuration_instance():
    """
    :return: a test instance of the configuration manager
    """
    property_configuration_manager = PropertyConfiguration(
        override_file_path='app/properties_configuration/tests/data/test_override.yml'
    )

    return property_configuration_manager


def get_group_configuration_instance():
    """
    :return: a test instance of the configuration manager
    """
    configuration_manager = get_property_configuration_instance()

    group_configuration_manager = GroupConfiguration(
        groups_file_path='app/properties_configuration/tests/data/test_groups.yml',
        sorting_file_path='app/properties_configuration/tests/data/test_default_sorting.yml',
        property_configuration_manager=configuration_manager
    )

    return group_configuration_manager


class ConfigurationManagerTester(unittest.TestCase):
    """
    Class to test the configuration manager
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Getting one property
    # ------------------------------------------------------------------------------------------------------------------
    def test_fails_when_index_does_not_exist(self):
        """
        Tests that it raises an error when the index requested does not exist
        """
        configuration_manager = get_property_configuration_instance()

        index_name = 'does_not_exist'
        prop_id = '_metadata.assay_data.assay_subcellular_fraction'

        with self.assertRaises(PropertyConfiguration.PropertiesConfigurationManagerError,
                               msg='An exception must have been raised!'):
            configuration_manager.get_config_for_prop(index_name, prop_id)

    def test_fails_when_property_does_not_exist(self):
        """
        Tests that it raises an error when the property requested does not exist
        """
        configuration_manager = get_property_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        prop_id = 'does_not_exist'

        with self.assertRaises(PropertyConfiguration.PropertiesConfigurationManagerError,
                               msg='An exception must have been raised!'):
            configuration_manager.get_config_for_prop(index_name, prop_id)

    def test_gets_config_for_one_property_with_no_override(self):
        """
        Tests that gets config for one property with no override
        """
        configuration_manager = get_property_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        prop_id = '_metadata.assay_data.assay_subcellular_fraction'
        config_got = configuration_manager.get_config_for_prop(index_name, prop_id)

        self.assertEqual(config_got['index_name'], index_name)
        self.assertEqual(config_got['prop_id'], prop_id)
        self.assertEqual(config_got['type'], 'string')
        self.assertTrue(config_got['aggregatable'])
        self.assertEqual(config_got['label'], 'Assay Data Subcellular Fraction')
        self.assertEqual(config_got['label_mini'], 'As. Data Subc. Frct.')

    def test_gets_config_for_one_property_with_override(self):
        """
        Tests gets the correct config for a property with override
        """
        configuration_manager = get_property_configuration_instance()

        with open(configuration_manager.override_file_path) as override_file:
            override_config_must_be = yaml.load(override_file, Loader=yaml.FullLoader)

            es_index_prefix = RUN_CONFIG.get('es_index_prefix')
            index_name = f'{es_index_prefix}activity'
            prop_id = '_metadata.activity_generated.short_data_validity_comment'
            config_got = configuration_manager.get_config_for_prop(index_name, prop_id)

            property_config_must_be = override_config_must_be[index_name][prop_id]
            self.assertEqual(config_got['label'], property_config_must_be['label'],
                             'The label was not overridden properly!')
            self.assertEqual(config_got['label_mini'], property_config_must_be['label_mini'],
                             'The label mini was not overridden properly!')

    def test_gets_config_for_a_virtual_property(self):
        """
        Tests gets the correct config for a virtual property
        """

        configuration_manager = get_property_configuration_instance()

        with open(configuration_manager.override_file_path) as override_file:
            override_config_must_be = yaml.load(override_file, Loader=yaml.FullLoader)

            es_index_prefix = RUN_CONFIG.get('es_index_prefix')
            index_name = f'{es_index_prefix}molecule'

            prop_id = 'trade_names'
            config_got = configuration_manager.get_config_for_prop(index_name, prop_id)

            property_config_must_be = override_config_must_be[index_name][prop_id]
            self.assertEqual(config_got['prop_id'], prop_id,
                             'The prop_id was not set up properly!')
            self.assertEqual(config_got['based_on'], property_config_must_be['based_on'],
                             'The based_on was not set up properly!')
            self.assertEqual(config_got['label'], property_config_must_be['label'],
                             'The label was not set up properly!')
            self.assertFalse(config_got['aggregatable'], 'This property should not be aggregatable')

            self.assertEqual(config_got['is_virtual'], True,
                             'This is a virtual property!')
            self.assertEqual(config_got['is_contextual'], False,
                             'This is not a contextual property!')

    def test_gets_config_fails_for_a_virtual_property_based_on_non_existing_prop(self):
        """
        Tests that when a virtual non contextual property is based on a no existing property it fails
        """
        configuration_manager = get_property_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}molecule'
        prop_id = 'trade_names_wrong'

        with self.assertRaises(PropertyConfiguration.PropertiesConfigurationManagerError,
                               msg='An exception must have been raised!'):
            configuration_manager.get_config_for_prop(index_name, prop_id)

    def test_makes_sure_config_for_a_contextual_property_is_correct(self):
        """
        Makes sure it fails when a virtual contextual proeprty does not define type and aggregatability
        """
        configuration_manager = get_property_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}molecule'
        prop_id = '_context.similarity_wrong'

        with self.assertRaises(PropertyConfiguration.PropertiesConfigurationManagerError,
                               msg='This should have thrown an exception for a bad configuration!'):
            configuration_manager.get_config_for_prop(index_name, prop_id)

    def test_gets_config_for_a_contextual_property(self):
        """
        tests gets the config for a virtual contextual property
        """
        configuration_manager = get_property_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}molecule'

        prop_id = '_context.similarity'
        config_got = configuration_manager.get_config_for_prop(index_name, prop_id)

        self.assertEqual(config_got['prop_id'], prop_id,
                         'The prop_id was not set up properly!')

        self.assertFalse(config_got['aggregatable'])
        self.assertTrue(config_got['sortable'])
        self.assertEqual(config_got['type'], 'double')
        self.assertEqual(config_got['label'], 'Similarity')
        self.assertEqual(config_got['label_mini'], 'Similarity')

        self.assertEqual(config_got['is_virtual'], True, 'This is a virtual property!')
        self.assertEqual(config_got['is_contextual'], True, 'This is a contextual property!')

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
