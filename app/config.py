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

if not RUN_CONFIG.get('server_public_host'):
    RUN_CONFIG['server_public_host'] = '0.0.0.0:5000'