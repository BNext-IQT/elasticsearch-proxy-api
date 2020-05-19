"""
Module to test configuration manager
"""
import unittest

from app.properties_configuration.configuration_manager import PropertiesConfigurationManager


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
        print('configuration_manager: ', configuration_manager)

        index_name = 'does_not_exist'
        prop_id = '_metadata.assay_data.assay_subcellular_fraction'


        print('TEST!!!')
        with self.assertRaises(PropertiesConfigurationManager.PropertiesConfigurationManagerError,
                               msg='An exception should have been raised!'):
            configuration_manager.get_config_for_prop(index_name, prop_id)
