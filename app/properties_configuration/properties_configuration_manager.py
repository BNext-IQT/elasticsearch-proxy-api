"""
    Module tht handles the configuration of the properties for the interface
"""
import os.path

import yaml
from elasticsearch.exceptions import NotFoundError

from app.es_data import es_mappings
from app import app_logging
from app.cache import CACHE


class PropertyConfiguration:
    """
    Class that handles the configuration of the properties for the interface
    """

    class PropertiesConfigurationManagerError(Exception):
        """Base class for exceptions in the properties configuration."""

    class PropertiesConfigurationManagerWarning(Warning):
        """Base class for warnings in the properties configuration."""

    def __init__(self, override_file_path):
        """
        :param override_file_path: path of the yaml file with the override config of the properties
        """
        if not os.path.isfile(override_file_path):
            raise self.PropertiesConfigurationManagerError(f'The path {override_file_path} does not exist!')

        self.override_file_path = override_file_path

    def __repr__(self):

        return f'PropertyConfiguration-{self.override_file_path}'

    def get_config_for_prop(self, index_name, prop_id):
        """
        :param index_name: name of the index to which the property belongs
        :param prop_id: full path of the property, such as  '_metadata.assay_data.assay_subcellular_fraction'
        :return: a dict describing the configuration of a property
        """
        cache_key = f'config_for_{index_name}-{prop_id}'
        app_logging.debug(f'cache_key: {cache_key}')

        cache_response = CACHE.get(key=cache_key)
        if cache_response is not None:
            app_logging.debug(f'results were cached')
            return cache_response

        app_logging.debug(f'results were not cached')

        app_logging.debug(f'getting property config for {prop_id} of index {index_name}')
        es_property_description = self.get_property_base_es_description(index_name, prop_id)
        property_override_description = self.get_property_base_override_description(index_name, prop_id)
        config = self.get_merged_prop_config(index_name, prop_id, es_property_description,
                                             property_override_description)
        return config

    def get_property_base_es_description(self, index_name, prop_id):
        """
        :param index_name: name of the index to which the property belongs
        :param prop_id: full path of the property, such as  '_metadata.assay_data.assay_subcellular_fraction'
        :return: the base description of the property in es, None if mapping not found
        """
        try:
            base_property_description = es_mappings.get_simplified_property_mapping(index_name, prop_id)
            return base_property_description
        except NotFoundError as error:
            raise self.PropertiesConfigurationManagerError(f'There was an error while getting the config for '
                                                           f'prop {prop_id}, {index_name}: {str(error)}')

    def get_property_base_override_description(self, index_name, prop_id):
        """
        :param index_name: name of the index to which the property belongs
        :param prop_id: full path of the property, such as  '_metadata.assay_data.assay_subcellular_fraction'
        :return: the base description of the property in the override files, None if config not found
        """

        with open(self.override_file_path, 'rt') as override_file:
            config_override = yaml.load(override_file, Loader=yaml.FullLoader)
            if config_override is not None:
                index_override = config_override.get(index_name)
                if index_override is not None:
                    return index_override.get(prop_id)
            return None

    def get_merged_prop_config(self, index_name, prop_id, es_property_description, property_override_description):
        """
        :param index_name: name of the index to which the property belongs
        :param prop_id: full path of the property, such as  '_metadata.assay_data.assay_subcellular_fraction'
        :param es_property_description: dict describing the property taken from es
        :param property_override_description: dict describing the property taken from the override
        :return: the merged configuration between what was found in es and the override config
        """
        found_in_es = es_property_description is not None
        app_logging.debug(f'Property {prop_id} of index {index_name} found_in_es: {found_in_es}')
        found_in_override = property_override_description is not None
        app_logging.debug(f'Property {prop_id} of index {index_name} found_in_override: {found_in_override}')

        if not found_in_es and not found_in_override:
            raise self.PropertiesConfigurationManagerError(
                f'The property {prop_id} of index {index_name} does not exist in elasticsearch or as virtual property')

        is_virtual = not found_in_es and found_in_override
        app_logging.debug(f'Property {prop_id} of index {index_name} is_virtual: {is_virtual}')

        if not is_virtual:
            return {
                'index_name': index_name,
                'prop_id': prop_id,
                **es_property_description,
                **(property_override_description if property_override_description is not None else {})
            }

        base_config = {
            'index_name': index_name,
            'prop_id': prop_id,
            'is_virtual': True
        }

        based_on = property_override_description.get('based_on')

        is_contextual = based_on is None
        app_logging.debug(f'Property {prop_id} of index {index_name} is_contextual: {is_contextual}')

        if not is_contextual:
            app_logging.debug(f'Property {prop_id} of index {index_name} based_on: {based_on}')
            return self.get_virtual_non_contextual_property_config(base_config, based_on, property_override_description)

        return self.get_virtual_contextual_property_config(base_config, property_override_description)

    def get_virtual_non_contextual_property_config(self, base_config, based_on, property_override_description):
        """
        A virtual property is such that does not have definition in es, a virtual - non contextual property is such that
        is based on an existing property in es. E.g. trade_names which does not exist in elasticsearch
        but is based on molecule_synonyms
        :param base_config: the basic configuration of the property with index name and prop id
        :param based_on: the id of the property on which it is based, it must be from the same index
        :param property_override_description: override config of the property
        :return: the configuration of the property
        """
        index_name = base_config['index_name']
        config_of_based_on_property = self.get_config_for_prop(index_name, based_on)

        return {
            **config_of_based_on_property,
            **base_config,
            **property_override_description,
            'is_contextual': False,
            'based_on': based_on
        }

    def get_virtual_contextual_property_config(self, base_config, property_override_description):
        """
        A virtual property is such that does not have definition in es, a virtual - contextual property is such that
        is NOT based on an existing property in es. E.g. similarity
        :param base_config: the basic configuration of the property with index name and prop id
        :param property_override_description: override config of the property
        :return: the configuration of the property
        """

        if property_override_description.get('aggregatable') is None or \
                        property_override_description.get('type') is None or \
                        property_override_description.get('sortable') is None:
            raise self.PropertiesConfigurationManagerError(
                f'A virtual contextual property must define the type and if it is '
                'aggregatable and sortable. index => {index_name} : prop => {prop_id}'
            )

        return {
            **base_config,
            **property_override_description,
            'is_contextual': True,
        }
