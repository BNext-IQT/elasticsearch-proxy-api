"""
Properties configuration service
"""
from app.properties_configuration import properties_configuration_manager
from app.properties_configuration import groups_configuration_manager
from app.properties_configuration import facets_groups_configuration_manager


class PropertiesConfigServiceError(Exception):
    """Base class for exceptions in the properties configuration service."""


def get_property_config(index_name, property_id):
    """
    :param index_name: name of the index to which the property belongs
    :param property_id: id of the property to check
    :return: the json with the property configuration
    """

    property_configuration_manager = properties_configuration_manager.get_property_configuration_instance()

    try:

        return property_configuration_manager.get_config_for_prop(index_name, property_id)

    except (properties_configuration_manager.PropertyConfiguration.PropertiesConfigurationManagerError,
            groups_configuration_manager.GroupConfiguration.GroupsConfigurationManagerError) as error:

        raise PropertiesConfigServiceError(repr(error))


def get_group_config(index_name, group_name):
    """
    :param index_name: name of the index to which the group belongs
    :param group_name: name of the group to check
    :return: the json with the group configuration
    """

    group_configuration_manager = groups_configuration_manager.get_groups_configuration_instance()

    try:

        return group_configuration_manager.get_config_for_group(index_name, group_name)

    except (properties_configuration_manager.PropertyConfiguration.PropertiesConfigurationManagerError,
            groups_configuration_manager.GroupConfiguration.GroupsConfigurationManagerError) as error:

        raise PropertiesConfigServiceError(repr(error))


def get_facets_group_config(index_name, group_name):
    """
    :param index_name: name of the index to which the group belongs
    :param group_name: name of the group to check
    :return: the json with the group configuration
    """

    facets_group_configuration_manager = facets_groups_configuration_manager.get_facets_groups_configuration_instance()

    try:

        return facets_group_configuration_manager.get_facets_config_for_group(index_name, group_name)

    except (properties_configuration_manager.PropertyConfiguration.PropertiesConfigurationManagerError,
            facets_group_configuration_manager.GroupConfiguration.FacetsGroupsConfigurationManagerError) as error:

        raise PropertiesConfigServiceError(repr(error))
