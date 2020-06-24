"""
    Module tht handles the configuration of the groups of properties for the interface
"""
import os

import yaml

from app import app_logging
from app import cache
from app.config import RUN_CONFIG
from app.properties_configuration import properties_configuration_manager


class GroupConfiguration:
    """
    Class that handles the configuration of the groups of properties for the interface
    """

    class GroupsConfigurationManagerError(Exception):
        """Base class for exceptions in the groups configuration."""

    def __init__(self, groups_file_path, sorting_file_path, property_configuration_manager):
        """
        :param groups_file_path: path of the yaml file with the groups config of the properties
        :param sorting_file_path: path of the yaml file with the sorting config of the properties
        :param property_configuration_manager: instance of the properties configuration manager
        """
        for path in [groups_file_path, sorting_file_path]:
            if not os.path.isfile(path):
                raise self.GroupsConfigurationManagerError(f'The path {path} does not exist!')

        self.groups_file_path = groups_file_path
        self.sorting_file_path = sorting_file_path
        self.property_configuration_manager = property_configuration_manager

    # ------------------------------------------------------------------------------------------------------------------
    # Getting a custom list of properties
    # ------------------------------------------------------------------------------------------------------------------
    def get_config_for_props_list(self, index_name, prop_ids):
        """
        :param index_name: name of the index
        :param prop_ids: list of ids of the properties to check
        :return: a list of configuration of the properties
        """
        configs = []

        for prop_id in prop_ids:
            configs.append(self.property_configuration_manager.get_config_for_prop(index_name, prop_id))

        return configs

    # ------------------------------------------------------------------------------------------------------------------
    # Getting a group of properties
    # ------------------------------------------------------------------------------------------------------------------
    def get_config_for_group(self, index_name, group_name):
        """
        :param index_name: name of the index
        :param group_name: group name as defined in the groups file
        :return: the configuration of the group with the following structure:
        {
            "properties": {
                "default": [...], # properties to show by default
                "optional:" [...] # properties to show as optional for the user
            }
        }
        """

        cache_key = f'config_for_group_{index_name}-{group_name}'
        app_logging.debug(f'cache_key: {cache_key}')

        cache_response = cache.fail_proof_get(key=cache_key)
        if cache_response is not None:
            app_logging.debug(f'results were cached')
            return cache_response

        app_logging.debug(f'results were not cached')

        with open(self.groups_file_path, 'rt') as groups_file:

            groups_config = yaml.load(groups_file, Loader=yaml.FullLoader)

            index_groups = groups_config.get(index_name, {})
            group_config = index_groups.get(group_name)
            if group_config is None:
                raise self.GroupsConfigurationManagerError(
                    f'The group {group_name} does not exist in index {index_name}!')

            props_configs = {}

            for sub_group, props_list in group_config.items():
                props_configs[sub_group] = self.get_config_for_props_list(index_name, props_list)

            config = {'properties': props_configs}

        seconds_valid = RUN_CONFIG.get('es_proxy_cache_seconds')
        cache.fail_proof_set(key=cache_key, value=config, timeout=seconds_valid)

        return config


def get_groups_configuration_instance():
    """
    :return: a default instance for the groups configuration
    """
    property_configuration_manager = properties_configuration_manager.get_property_configuration_instance()

    group_configuration_manager = GroupConfiguration(
        groups_file_path='app/properties_configuration/config/groups.yml',
        sorting_file_path='app/properties_configuration/config/default_sorting.yml',
        property_configuration_manager=property_configuration_manager
    )

    return group_configuration_manager
