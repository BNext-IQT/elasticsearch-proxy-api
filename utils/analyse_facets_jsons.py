from os import listdir
import json

jsons_path = 'app/properties_configuration/config/temp'

config_keys = set()

for file_path in listdir(jsons_path):

    print('going to read file: ', file_path)
    with open(f'{jsons_path}/{file_path}', 'rt') as json_file:
        facets_final_config = json.loads(json_file.read())

        for item_key, config_value in facets_final_config.items():

            print(set(config_value.keys()))
            config_keys |= set(config_value.keys())


print('config_keys: ')
print(config_keys)
