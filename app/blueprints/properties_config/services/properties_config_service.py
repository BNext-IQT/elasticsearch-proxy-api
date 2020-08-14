"""
Properties configuration service
"""
from app.properties_configuration import properties_configuration_manager
from app.properties_configuration import groups_configuration_manager
from app.properties_configuration import facets_groups_configuration_manager
from app.es_data import es_mappings


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
            facets_groups_configuration_manager.FacetsGroupsConfiguration.FacetsGroupsConfigurationManagerError) \
            as error:

        raise PropertiesConfigServiceError(repr(error))


def get_index_properties_of_index(index_name):
    """
    :param index_name: name of the index to get the id properties
    :return: a dict with the id properties of the index
    """

    try:

        id_properties = es_mappings.get_id_properties_for_index(index_name)
        return {
            'id_properties': id_properties
        }

    except es_mappings.EsMappingsError as error:

        raise PropertiesConfigServiceError(repr(error))


def get_all_configured_properties_for_index(index_name):
    """
    :param index_name: name of the index to get the all the properties configuration
    :return: a dict with the configurations
    """

    try:

        group_configuration_manager = groups_configuration_manager.get_groups_configuration_instance()
        props_list_from_groups = group_configuration_manager.get_list_of_configured_properties(index_name)

        facets_group_configuration_manager = \
            facets_groups_configuration_manager.get_facets_groups_configuration_instance()
        props_list_from_facets_groups = \
            facets_group_configuration_manager.get_list_of_configured_properties(index_name)

        all_props = list(set(props_list_from_groups).union(set(props_list_from_facets_groups)))

        return {
            'all_properties': all_props
        }

    except es_mappings.EsMappingsError as error:

        raise PropertiesConfigServiceError(repr(error))
