from os import listdir
import json
import yaml

def get_or_create(dictionary, key_name):

    value = dictionary.get(key_name)
    if value is None:
        dictionary[key_name] = {}
    return dictionary[key_name]

jsons_path = 'app/properties_configuration/config/temp'
yaml_destination = 'app/properties_configuration/config/facets_groups.yml'

config_keys = set()
generated_config = {}
num_properties_analysed = 0

for file_path in listdir(jsons_path):

    print('going to read file: ', file_path)
    with open(f'{jsons_path}/{file_path}', 'rt') as json_file:
        facets_final_config = json.loads(json_file.read())

        for item_key, source_config_value in facets_final_config.items():
            num_properties_analysed += 1
            config_keys |= set(source_config_value.keys())

            index_name = source_config_value['es_index'].replace('27_', '')
            index_config = get_or_create(generated_config, index_name)

            group_name = 'browser_facets'
            group_config = get_or_create(index_config, group_name)
            is_default = source_config_value['show'] == True
            if is_default:
                properties_config = get_or_create(group_config, 'default')
            else:
                properties_config = get_or_create(group_config, 'optional')

            initial_sort = source_config_value.get('initial_sort')
            initial_intervals = source_config_value.get('initial_intervals')
            has_default_agg_config = initial_sort is None and initial_intervals is None

            if has_default_agg_config:

                property_config = {
                    'agg_type': 'terms',
                    'agg_params': {}
                }

            else:

                property_config = {
                    'agg_type': 'terms',
                    'agg_params': {
                      'initial_sort': initial_sort,
                      'initial_intervals': initial_intervals
                    }
                }

            properties_config[item_key] = property_config

print('config_keys: ')
print(config_keys)

print('generated_config')
print(json.dumps(generated_config, indent=4))

print('num_properties_analysed: ', num_properties_analysed)

with open(yaml_destination, 'w') as output_file:
    yaml.dump(generated_config, output_file)
