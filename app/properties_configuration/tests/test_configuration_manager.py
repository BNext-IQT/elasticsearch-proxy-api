"""
Module to test configuration manager
"""
import unittest

import yaml

from app.properties_configuration.configuration_manager import PropertiesConfigurationManager
from app.config import RUN_CONFIG


# ------------------------------------------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------------------------------------------
def get_config_manager_instance():
    """
    :return: a test instance of the configuration manager
    """
    configuration_manager = PropertiesConfigurationManager(
        override_file_path='app/properties_configuration/tests/data/test_override.yml',
        groups_file_path='app/properties_configuration/tests/data/test_groups.yml',
        sorting_file_path='app/properties_configuration/tests/data/test_default_sorting.yml'
    )

    return configuration_manager


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
        configuration_manager = get_config_manager_instance()

        index_name = 'does_not_exist'
        prop_id = '_metadata.assay_data.assay_subcellular_fraction'

        with self.assertRaises(PropertiesConfigurationManager.PropertiesConfigurationManagerError,
                               msg='An exception must have been raised!'):
            configuration_manager.get_config_for_prop(index_name, prop_id)

    def test_fails_when_property_does_not_exist(self):
        """
        Tests that it raises an error when the property requested does not exist
        """
        configuration_manager = get_config_manager_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}activity'
        prop_id = 'does_not_exist'

        with self.assertRaises(PropertiesConfigurationManager.PropertiesConfigurationManagerError,
                               msg='An exception must have been raised!'):
            configuration_manager.get_config_for_prop(index_name, prop_id)

    def test_gets_config_for_one_property_with_no_override(self):
        """
        Tests that gets config for one property with no override
        """
        configuration_manager = get_config_manager_instance()

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
        Tests gets the correct config dor a property with override
        """
        configuration_manager = get_config_manager_instance()

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
