#!/usr/bin/env python3
"""
Script that tests queries with many ids and generates csv file with the result
"""
# pylint: disable=too-many-locals
import argparse
import json
import time

from elasticsearch import Elasticsearch

PARSER = argparse.ArgumentParser()
PARSER.add_argument('es_host', help='Elastichsearch host to use',
                    default='http://127.0.0.1:5000', nargs='?')
PARSER.add_argument('es_port', help='ES username',
                    default='admin', nargs='?')
PARSER.add_argument('es_username', help='ES username',
                    default='admin', nargs='?')
PARSER.add_argument('es_password', help='ES password',
                    default='123456', nargs='?')
ARGS = PARSER.parse_args()


def run():
    """
    Runs the script
    """
    es_conn = Elasticsearch(
        [ARGS.es_host],
        http_auth=(ARGS.es_username, ARGS.es_password),
        port=ARGS.es_port
    )

    print('GOING TO LOAD MOLECULE CHEMBL IDS...')

    with open('utils/data/chembl_ids.json') as json_file:
        all_ids = json.load(json_file)

    output_file_name = 'output.csv'
    with open(output_file_name, 'wt') as output_file:
        output_file.write('num_ids;time_with_terms\n')

    all_ids.reverse()
    num_all_compounds = len(all_ids)
    print(f'LOADED {num_all_compounds} compounds')
    numbers = [int((percentage * num_all_compounds) / 100) for percentage in range(1, 101)]
    numbers.insert(0, 5)
    numbers.insert(1, 500)
    numbers.insert(2, 1000)
    numbers.insert(3, 1024)
    numbers.insert(4, 1025)

    for num_compounds in numbers:
        start = 0
        end = start + num_compounds
        ids = all_ids[start:end]

        terms_query = get_terms_filter_query(ids)

        print('---')
        print('With {} compounds'.format(num_compounds))

        start_time = time.time()
        res = es_conn.search(index="chembl_26_activity", body={"query": terms_query})
        end_time = time.time()
        time_taken_terms = end_time - start_time

        print(f'Num results terms: {res["hits"]["total"]}')
        print(f'total time terms: {time_taken_terms}')

        script_query = get_script_query(ids)

        start_time = time.time()
        res = es_conn.search(index="chembl_26_activity", body={"query": script_query})
        end_time = time.time()
        time_taken_script = end_time - start_time

        print(f'Num results script: {res["hits"]["total"]}')
        print(f'total time script: {time_taken_script}')

        with open(output_file_name, 'at') as output_file:
            output_file.write(f'{num_compounds};{time_taken_terms};{time_taken_script}\n')



def get_terms_filter_query(ids):
    """
    :param ids: list of ids
    :return: the terms filter query
    """
    return {
        "bool": {
            "filter": {
                "terms": {
                    "molecule_chembl_id": ids
                }
            }
        }
    }


def get_script_query(ids):
    """
    :param ids: list of ids
    :return: the script query
    """
    chembl_ids_index = {}
    for chembl_id in ids:
        chembl_ids_index[chembl_id] = True

    return {
        "bool": {
            "filter": {
                "script": {
                    "script": {
                        "source": "params.chembl_ids.containsKey(doc['molecule_chembl_id'].value)",
                        "lang": "painless",
                        "params": {
                            "chembl_ids": chembl_ids_index
                        }
                    }
                }
            }
        }
    }


if __name__ == "__main__":
    run()
