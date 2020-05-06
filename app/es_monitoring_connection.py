"""
Module that handles the connection with the elasticsearch used for monitoring
"""
from elasticsearch import Elasticsearch
from app.config import RUN_CONFIG

ES_MONITORING = Elasticsearch(
    [RUN_CONFIG.get('usage_statistics', {}).get('elasticsearch').get('host')],
    http_auth=(RUN_CONFIG.get('usage_statistics', {}).get('elasticsearch').get('username'),
               RUN_CONFIG.get('usage_statistics', {}).get('elasticsearch').get('password')),
    port=RUN_CONFIG.get('usage_statistics', {}).get('elasticsearch').get('port')
)
