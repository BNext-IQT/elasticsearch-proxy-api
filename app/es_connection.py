"""
Module that handles the connection with elasticsearch
"""
from elasticsearch import Elasticsearch
from app.config import RUN_CONFIG

ES = Elasticsearch(
    [RUN_CONFIG.get('elasticsearch').get('host')],
    http_auth=(RUN_CONFIG.get('elasticsearch').get('username'), RUN_CONFIG.get('elasticsearch').get('password')),
    port=RUN_CONFIG.get('elasticsearch').get('port'),
    timeout=RUN_CONFIG.get('elasticsearch').get('timeout', 10),
    retry_on_timeout=RUN_CONFIG.get('elasticsearch').get('retry_on_timeout', False),
)
