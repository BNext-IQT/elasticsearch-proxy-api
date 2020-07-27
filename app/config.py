"""
    Module that handles the configuration of the app
"""
import os
from pathlib import Path
import hashlib
from enum import Enum
import yaml

CUSTOM_CONFIG_FILE_PATH = os.getenv('CONFIG_FILE_PATH')
if CUSTOM_CONFIG_FILE_PATH is not None:
    CONFIG_FILE_PATH = CUSTOM_CONFIG_FILE_PATH
else:
    CONFIG_FILE_PATH = str(Path().absolute()) + '/config.yml'

print('------------------------------------------------------------------------------------------------')
print('CONFIG_FILE_PATH: ', CONFIG_FILE_PATH)
print('------------------------------------------------------------------------------------------------')


class ImproperlyConfiguredError(Exception):
    """Base class for exceptions in this module."""


class RunEnvs(Enum):
    """
        Class that defines the possible run environments
    """
    DEV = 'DEV'
    TEST = 'TEST'
    STAGING = 'STAGING'
    PROD = 'PROD'

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def hash_secret(secret):
    """
    Returns a a digest of a secret you want to store in memory
    :param secret: secret you want to hash
    :return: a sha256 hash of the secret, encoded in hexadecimal
    """

    hashed = hashlib.sha256(secret.encode('UTF-8')).hexdigest()
    return hashed


def verify_secret(prop_name, value):
    """
    Verifies that a value in the current config (hashed) corresponds to the value passed as parameter (unhashed)
    :param prop_name: name of the property in the configuration
    :param value: clear text value of the property.
    :return: True if the value is correct, false otherwise
    """

    hashed = hashlib.sha256(value.encode('UTF-8')).hexdigest()
    has_must_be = RUN_CONFIG.get(prop_name)

    return hashed == has_must_be


print('Loading run config')
try:
    RUN_CONFIG = yaml.load(open(CONFIG_FILE_PATH, 'r'), Loader=yaml.FullLoader)
    print('Run config loaded')
except FileNotFoundError:
    print('Config file not found. Attempting to load config from environment variable DELAYED_JOBS_RAW_CONFIG')
    RAW_CONFIG = os.getenv('DELAYED_JOBS_RAW_CONFIG')
    print('raw_config: ', RAW_CONFIG)
    RUN_CONFIG = yaml.load(RAW_CONFIG, Loader=yaml.FullLoader)

# Load defaults
ES_CONFIG = RUN_CONFIG.get('elasticsearch', {})
DEFAULT_ES_CONFIG = {
    'host': 'https://www.ebi.ac.uk/chembl/glados-es'

}
RUN_CONFIG['elasticsearch'] = {
    **DEFAULT_ES_CONFIG,
    **ES_CONFIG,
}

CACHE_CONFIG = RUN_CONFIG.get('cache_config', {})
DEFAULT_CACHE_CONFIG = {
    'CACHE_TYPE': 'simple'
}
RUN_CONFIG['cache_config'] = {
    **DEFAULT_CACHE_CONFIG,
    **CACHE_CONFIG,
}

if RUN_CONFIG.get('base_path') is None:
    RUN_CONFIG['base_path'] = ''

if RUN_CONFIG.get('es_proxy_cache_seconds') is None:
    RUN_CONFIG['es_proxy_cache_seconds'] = 604800

if RUN_CONFIG.get('es_mappings_cache_seconds') is None:
    RUN_CONFIG['es_mappings_cache_seconds'] = 86400

if RUN_CONFIG.get('filter_query_max_clauses') is None:
    RUN_CONFIG['filter_query_max_clauses'] = 30000

DELAYED_JOBS_CONFIG = RUN_CONFIG.get('delayed_jobs', {})
DEFAULT_DELAYED_JOBS_CONFIG = {
    'wwwdev.ebi.ac.uk': 'wwwdev.ebi.ac.uk',
    'www.ebi.ac.uk': 'www.ebi.ac.uk'
}
RUN_CONFIG['delayed_jobs'] = {
    **DEFAULT_DELAYED_JOBS_CONFIG,
    **DELAYED_JOBS_CONFIG,
}

if not RUN_CONFIG.get('server_public_host'):
    RUN_CONFIG['server_public_host'] = '0.0.0.0:5000'

URL_SHORTENING_CONFIG = RUN_CONFIG.get('url_shortening', {})
DEFAULT_URL_SHORTENING_CONFIG = {
    'days_valid': 7,
    'dry_run': True,
    'keep_alive': True,
    'keep_alive_days': 1,
    'index_name': 'some_index',
    'statistics_index_name': 'some_index',
    'expired_urls_lazy_deletion_threshold': 1000
}
RUN_CONFIG['url_shortening'] = {
    **DEFAULT_URL_SHORTENING_CONFIG,
    **URL_SHORTENING_CONFIG,
}

DEFAULT_LAZY_OLD_RECORD_DELETION_CONFIG = {
    'delete_records_older_than_days': 365,
    'expired_docs_lazy_deletion_threshold': 1000,
    'index_names_and_timestamps': []
}

LAZY_OLD_RECORD_DELETION_CONFIG = RUN_CONFIG.get('lazy_old_record_deletion', {})
RUN_CONFIG['lazy_old_record_deletion'] = {
    **DEFAULT_LAZY_OLD_RECORD_DELETION_CONFIG,
    **LAZY_OLD_RECORD_DELETION_CONFIG
}

CHEMBL_API_CONFIG = RUN_CONFIG.get('chembl_api', {})
DEFAULT_CHEMBL_API_CONFIG = {
    'ws_url': 'https://www.ebi.ac.uk/chembl/api/data'
}
RUN_CONFIG['chembl_api'] = {
    **CHEMBL_API_CONFIG,
    **DEFAULT_CHEMBL_API_CONFIG,
}
