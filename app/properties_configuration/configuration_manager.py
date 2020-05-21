"""
    Module tht handles the configuration of the properties for the interface
"""
import yaml
import warnings
import os.path

from elasticsearch.exceptions import NotFoundError

from app.es_data import es_mappings
from app import app_logging


class PropertiesConfigurationManager:
    """
    Class that handles the configuration of the properties for the interface
    """

    class PropertiesConfigurationManagerError(Exception):
        """Base class for exceptions in the properties configuration."""
        pass

    class PropertiesConfigurationManagerWarning(Warning):
        """Base class for warnings in the properties configuration."""
        pass

    def __init__(self, override_file_path, groups_file_path, sorting_file_path):
        """
        :param override_file_path: path of the yaml file with the override config of the properties
        :param groups_file_path: path of the yaml file with the groups config of the properties
        :param sorting_file_path: path of the yaml file with the sorting config of the properties
        """
        for path in [override_file_path, groups_file_path, sorting_file_path]:
            if not os.path.isfile(path):
                raise self.PropertiesConfigurationManagerError(f'The path {path} does not exist!')

        self.override_file_path = override_file_path
        self.groups_file_path = groups_file_path
        self.sorting_file_path = sorting_file_path

    def __repr__(self):

        return f'{self.override_file_path}-{self.groups_file_path}-{self.sorting_file_path}'

    def get_config_for_prop(self, index_name, prop_id):
        """
        :param index_name: name of the index to which the property belongs
        :param prop_id: full path of the property, such as  '_metadata.assay_data.assay_subcellular_fraction'
        :return: a dict describing the configuration of a property
        """
        app_logging.debug(f'getting property config for {prop_id} of index {index_name}')
        es_property_description = self.get_property_base_es_description(index_name, prop_id)

        found_in_es = es_property_description is not None
        app_logging.debug(f'found_in_es: {found_in_es}')
        if not found_in_es:
            es_property_description = {}

        property_override_description = self.get_property_base_override_description(index_name, prop_id)
        found_in_override = property_override_description is not None
        app_logging.debug(f'found_in_override: {found_in_override}')

        if not found_in_es and not found_in_override:
            raise self.PropertiesConfigurationManagerError(
                f'The property {prop_id} does not exist in elasticsearch or as virtual property')

        config = get_merged_prop_config(index_name, prop_id, es_property_description, property_override_description)
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

def get_merged_prop_config(index_name, prop_id, es_property_description, property_override_description):
    """
    :param index_name: name of the index to which the property belongs
    :param prop_id: full path of the property, such as  '_metadata.assay_data.assay_subcellular_fraction'
    :param es_property_description: dict describing the property taken from es
    :param property_override_description: dict describing the property taken from the override
    :return: the merged configuration between what was found in es and the override config
    """
    found_in_es = es_property_description is not None
    found_in_override = property_override_description is not None

    is_virtual = not found_in_es and found_in_override

    if not is_virtual:

        return {
            'index_name': index_name,
            'prop_id': prop_id,
            **es_property_description,
            **(property_override_description if property_override_description is not None else {})
        }

    return {}

def get_config_for_prop(index_name, prop_id):
    cache_key = 'property_config-{index_name}-{prop_id}'.format(index_name=index_name, prop_id=prop_id)
    cache_response = cache.get(cache_key)
    if cache_response is not None:
        return cache_response

    index_mapping = resources_description.RESOURCES_BY_IDX_NAME.get(index_name)
    if index_mapping is None:
        raise ESPropsConfigurationManagerError("The index {} does not exist!".format(index_name))

    simplified_mapping = index_mapping.get_simplified_mapping_from_es()
    es_property_description = simplified_mapping.get(prop_id)

    found_in_es = es_property_description is not None
    if not found_in_es:
        es_property_description = {}

    # Search for description in override
    config_override = yaml.load(open(settings.PROPERTIES_CONFIG_OVERRIDE_FILE, 'r'), Loader=yaml.FullLoader)
    found_in_override = False
    if config_override is not None:
        index_override = config_override.get(index_name)
        if index_override is not None:
            property_override_description = index_override.get(prop_id)
            found_in_override = property_override_description is not None

    config = {}
    if not found_in_es and not found_in_override:
        raise ESPropsConfigurationManagerError("The property {} does not exist in elasticsearch or as virtual property"
                                               .format(prop_id))

    elif found_in_es and not found_in_override:
        # this is a normal property WITHOUT override

        config = SummableDict({
            'index_name': index_name,
            'prop_id': prop_id,
        })
        config += SummableDict(es_property_description)

    elif not found_in_es and found_in_override:
        # this is a virtual property
        config = SummableDict({
            'index_name': index_name,
            'prop_id': prop_id,
            'is_virtual': True
        })

        based_on = property_override_description.get('based_on')
        if based_on is not None:
            config['is_contextual'] = False
            base_description = simplified_mapping.get(based_on)
            if base_description is None:
                raise ESPropsConfigurationManagerError(
                    'The virtual property {prop_id} is based on {based_on} which does not exist in elasticsearch '
                    'index {index_name}'.format(prop_id=prop_id, based_on=based_on, index_name=index_name))
            config += SummableDict(base_description)

        else:
            config['is_contextual'] = True
            if property_override_description.get('aggregatable') is None or \
                            property_override_description.get('type') is None or \
                            property_override_description.get('sortable') is None:
                raise ESPropsConfigurationManagerError('A contextual property must define the type and if it is '
                                                       'aggregatable and sortable. index => {} : prop => {}'
                                                       .format(index_name, prop_id))

        config += property_override_description

    elif found_in_es and found_in_override:
        # this is a normal overridden property
        config = SummableDict({
            'index_name': index_name,
            'prop_id': prop_id,
        })
        config += SummableDict(es_property_description)
        config += property_override_description

    cache.set(cache_key, config, CACHE_TIME)
    return config


def get_config_for_props_list(index_name, prop_ids):
    configs = []

    for prop_id in prop_ids:
        configs.append(get_config_for_prop(index_name, prop_id))

    return configs


def get_config_for_group(index_name, group_name):
    groups_config = yaml.load(open(settings.PROPERTIES_GROUPS_FILE, 'r'), Loader=yaml.FullLoader)
    if groups_config is None:
        raise ESPropsConfigurationManagerError("There is no configuration for groups. "
                                               "There should be a configuration set up in {}"
                                               .format(settings.PROPERTIES_GROUPS_FILE))

    index_mapping = resources_description.RESOURCES_BY_IDX_NAME.get(index_name)
    if index_mapping is None:
        raise ESPropsConfigurationManagerError("The index {} does not exist!".format(index_name))

    index_groups = groups_config.get(index_name, {})
    group_config = index_groups.get(group_name)
    if group_config is None:
        raise ESPropsConfigurationManagerError("The group {} does not exist!".format(group_name))

    props_configs = {}

    for sub_group, props_list in group_config.items():
        props_configs[sub_group] = get_config_for_props_list(index_name, props_list)

    config = {'properties': props_configs}

    sorting_config = yaml.load(open(settings.GROUPS_DEFAULT_SORTING_FILE, 'r'), Loader=yaml.FullLoader)
    if sorting_config is not None:
        index_sorting = sorting_config.get(index_name)
        if index_sorting is not None:
            group_sorting = index_sorting.get(group_name)
            if group_sorting is not None:
                config['default_sorting'] = group_sorting

    return config


def get_id_property_for_index(index_name):
    resources_desc = resources_description.RESOURCES_BY_IDX_NAME
    resource_desc = resources_desc.get(index_name)
    if resource_desc is None:
        raise ESPropsConfigurationManagerError('The index {} does not exist.'.format(index_name))

    resource_ids = resource_desc.resource_ids
    if len(resource_ids) > 1:
        warnings.warn('The index {} has a compound id (domposed by more than one property). '
                      'Which is not fully supported yet'.format(index_name), ESPropsConfigurationManagerWarning)

    return resource_ids[0]


# -----------------------------------------------------------------------------------
# Properties counts
# -----------------------------------------------------------------------------------

def print_properties_counts():
    es_util.setup_connection_from_full_url(settings.ELASTICSEARCH_HOST)
    print()
    print_groups_counts()
    print()
    print_props_counts()


def print_props_counts():
    print('Props Counts:')
    groups_config = yaml.load(open(settings.PROPERTIES_GROUPS_FILE, 'r'), Loader=yaml.FullLoader)

    groups_properties = []

    index_name_label = 'Index Name'
    total_properties_label = 'Total Properties'
    num_used_properties_label = 'Used Properties'

    all_labels = [index_name_label, total_properties_label, num_used_properties_label]

    for index_name, index_mapping in resources_description.RESOURCES_BY_IDX_NAME.items():

        mapping = index_mapping.get_resource_mapping_from_es()
        current_index_description = {
            index_name_label: index_name,
            total_properties_label: get_num_properties_in_dict(mapping),
            num_used_properties_label: 0
        }
        groups_properties.append(current_index_description)
        index_groups = groups_config.get(index_name, {})

        used_properties = set()
        for group_name, group in index_groups.items():
            for sub_group, props_list in group.items():
                for prop in props_list:
                    used_properties.add(prop)

        current_index_description[num_used_properties_label] = len(used_properties)

    print_table(groups_properties, all_labels)


def print_groups_counts():
    print('Groups Counts:')

    groups_config = yaml.load(open(settings.PROPERTIES_GROUPS_FILE, 'r'), Loader=yaml.FullLoader)
    groups_properties = []

    index_name_label = 'Index Name'
    groups_and_subgroups_label = 'Groups'
    total_groups_label = 'Total Groups'
    all_labels = [index_name_label, groups_and_subgroups_label, total_groups_label]

    for index_name, index_mapping in resources_description.RESOURCES_BY_IDX_NAME.items():

        current_index_description = {
            index_name_label: index_name,
            groups_and_subgroups_label: '',
            total_groups_label: 0
        }
        groups_properties.append(current_index_description)

        index_groups = groups_config.get(index_name, {})
        all_groups_texts = []

        for group_name, group in index_groups.items():

            properties_in_group = 0
            all_subgroups = []

            for sub_group, props_list in group.items():
                all_subgroups.append(sub_group)
                num_properties_in_subgroup = len(props_list)

                properties_in_group += num_properties_in_subgroup

            current_group_text = '{group_name}({sub_groups})'.format(group_name=group_name,
                                                                     sub_groups=', '.join(all_subgroups))
            all_groups_texts.append(current_group_text)

        current_index_description[groups_and_subgroups_label] = ' '.join(all_groups_texts)
        current_index_description[total_groups_label] = len(all_groups_texts)

    print_table(groups_properties, all_labels)


def print_table(rows, labels):
    header_line = '\t'.join(labels)
    print(header_line)

    for row in rows:
        row_line = '\t'.join([str(row.get(label, '')) for label in labels])
        print(row_line)


# this counts the leaves of a dict
def get_num_properties_in_dict(d):
    # anything that is not dict is a leave
    if not isinstance(d, dict):
        return 1
    # empty dicts are leaves
    elif len(d.keys()) == 0:
        return 1
    # if I am not leave, the number of leaves is the sum of leaves of in my children
    else:
        return sum([get_num_properties_in_dict(sub_d) for sub_d in d.values()])
