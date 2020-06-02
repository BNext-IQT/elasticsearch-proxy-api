"""
    Module that handles the configuration of the groups of facets for the interface
"""
import os

import yaml

from app.properties_configuration import properties_configuration_manager
from app.cache import CACHE
from app import app_logging
from app.config import RUN_CONFIG


class FacetsGroupsConfiguration:
    """
    Class that handles the configuration of the groups of facets for the interface
    """

    class FacetsGroupsConfigurationManagerError(Exception):
        """Base class for exceptions in the facets groups configuration."""

    def __init__(self, facets_groups_file_path, property_configuration_manager):
        """
        :param facets_groups_file_path: path to the file where the facets groups config is
        :param property_configuration_manager: instance of the properties configuration manager
        """
        if not os.path.isfile(facets_groups_file_path):
            raise self.FacetsGroupsConfigurationManagerError(f'The path {facets_groups_file_path} does not exist!')

        self.facets_groups_file_path = facets_groups_file_path
        self.property_configuration_manager = property_configuration_manager

    def get_facets_config_for_group(self, index_name, group_name):
        """
        :param index_name: name of the index to which the group belongs
        :param group_name: name of the facets group
        :return: the configuration for the facets group
        """

        cache_key = f'facets_config_for_group_{index_name}-{group_name}'
        app_logging.debug(f'cache_key: {cache_key}')

        cache_response = CACHE.get(key=cache_key)
        if cache_response is not None:
            app_logging.debug(f'results were cached')
            return cache_response

        app_logging.debug(f'results were not cached')

        with open(self.facets_groups_file_path, 'rt') as groups_file:

            groups_config = yaml.load(groups_file, Loader=yaml.FullLoader)

            index_groups = groups_config.get(index_name)
            if index_groups is None:
                raise self.FacetsGroupsConfigurationManagerError(
                    f'The index {index_name} does not have a configuration set up!')

            group_config = index_groups.get(group_name)
            if group_config is None:
                raise self.FacetsGroupsConfigurationManagerError(
                    f'The group {group_name} does not exist in index {index_name}!')

            default_properties = group_config.get('default', {})
            optional_properties = group_config.get('optional', {})

        config = {
            'properties': {
                'default': self.get_facets_config_for_properties(default_properties, index_name),
                'optional': self.get_facets_config_for_properties(optional_properties, index_name)
            }
        }

        seconds_valid = RUN_CONFIG.get('es_proxy_cache_seconds')
        CACHE.set(key=cache_key, value=config, timeout=seconds_valid)
        return config

    def get_facets_config_for_properties(self, props_dict, index_name):
        """
        :param props_dict: dictionary with the properties configuration from yaml
        :param index_name: name of the index to which the group belongs
        :return: the facets config for the properties in the dict
        """
        description = []
        for prop_id, agg_config in props_dict.items():
            prop_config = self.property_configuration_manager.get_config_for_prop(index_name, prop_id)
            facet_config = {
                'prop_id': prop_id,
                'property_config': prop_config,
                'agg_config': agg_config
            }
            description.append(facet_config)

        return description


def get_facets_groups_configuration_instance():
    """
    :return: a default instance for the facets groups configuration
    """
    property_configuration_manager = properties_configuration_manager.get_property_configuration_instance()

    group_configuration_manager = FacetsGroupsConfiguration(
        facets_groups_file_path='app/properties_configuration/config/facets_groups.yml',
        property_configuration_manager=property_configuration_manager
    )

    return group_configuration_manager
