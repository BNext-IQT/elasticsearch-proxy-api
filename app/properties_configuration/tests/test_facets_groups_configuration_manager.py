"""
Module to test groups configuration manager
"""
import unittest

import yaml

from app.properties_configuration.tests import test_property_configuration_manager
from app.properties_configuration.facets_groups_configuration_manager import FacetsGroupsConfiguration
from app.config import RUN_CONFIG


def get_facets_groups_configuration_instance():
    """
    :return: a test instance of the facets configuration manager
    """
    configuration_manager = test_property_configuration_manager.get_property_configuration_instance()

    facets_groups_configuration_manager = FacetsGroupsConfiguration(
        facets_groups_file_path='app/properties_configuration/tests/data/test_facets_groups.yml',
        property_configuration_manager=configuration_manager
    )

    return facets_groups_configuration_manager


class FacetsGroupsConfigurationManagerTester(unittest.TestCase):
    """
    Class to test the facets configuration manager
    """

    def test_gets_config_for_a_group_fails_when_index_does_not_exist(self):
        """
        tests that getting config for a group fails when index does not exist
        """

        index_name = 'does_not_exist'
        group_name = 'download'

        facets_groups_configuration_manager = get_facets_groups_configuration_instance()

        with self.assertRaises(FacetsGroupsConfiguration.FacetsGroupsConfigurationManagerError,
                               msg='This should have thrown an exception for a non existing property!'):
            facets_groups_configuration_manager.get_facets_config_for_group(index_name, group_name)

    def test_gets_config_for_a_group_fails_when_group_does_not_exist(self):
        """
        tests that gets_config_for_a_group fails when group does not exist
        """

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}molecule'
        group_name = 'does_not_exist'

        facets_groups_configuration_manager = get_facets_groups_configuration_instance()
        with self.assertRaises(FacetsGroupsConfiguration.FacetsGroupsConfigurationManagerError,
                               msg='This should have thrown an exception for a non existing property!'):
            facets_groups_configuration_manager.get_facets_config_for_group(index_name, group_name)

    # pylint: disable=too-many-locals
    def test_gets_config_for_a_facets_group(self):
        """
        tests that gets config for a group with default and additional properties
        """
        facets_groups_configuration_manager = get_facets_groups_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}molecule'
        group_name = 'browser_facets'

        configs_got = facets_groups_configuration_manager.get_facets_config_for_group(index_name, group_name)[
            'properties']

        with open(facets_groups_configuration_manager.facets_groups_file_path, 'rt') as groups_config_file:
            groups_must_be = yaml.load(groups_config_file, Loader=yaml.FullLoader)
            group_must_be = groups_must_be[index_name][group_name]

            for type_key in ['default', 'optional']:
                properties_got = configs_got[type_key]
                properties_must_be = group_must_be[type_key]
                self.assertEqual(len(properties_got), len(properties_must_be), msg=f'{type_key} configs are missing!')

                for prop_desc in properties_got:
                    prop_id = prop_desc['prop_id']
                    agg_config_got = prop_desc['agg_config']
                    agg_config_must_be = properties_must_be[prop_id]

                    self.assertEqual(agg_config_got, agg_config_must_be,
                                     msg='The agg config was not generated properly!')

    def test_gets_all_configured_properties(self):
        """
        Tests that it returns all the configured properties for an index
        """
        facets_groups_configuration_manager = get_facets_groups_configuration_instance()

        es_index_prefix = RUN_CONFIG.get('es_index_prefix')
        index_name = f'{es_index_prefix}molecule'

        id_properties_must_be = ['molecule_type', 'max_phase', 'molecule_properties.hbd']
        id_properties_got = facets_groups_configuration_manager.get_list_of_configured_properties(index_name)

        self.assertEqual(sorted(id_properties_got), sorted(id_properties_must_be), msg='The properties list is not correct!')
