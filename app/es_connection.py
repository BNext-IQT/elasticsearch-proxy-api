"""
Module that handles the connection with elasticsearch
"""
import elasticsearch
from app.config import RUN_CONFIG

ELASTICSEARCH_HOST = RUN_CONFIG.get('elasticsearch').get('host')
ELASTICSEARCH_PORT = RUN_CONFIG.get('elasticsearch').get('port')
ELASTICSEARCH_USERNAME = RUN_CONFIG.get('elasticsearch').get('username')
ELASTICSEARCH_PASSWORD = RUN_CONFIG.get('elasticsearch').get('password')
ELASTICSEARCH_TIMEOUT = RUN_CONFIG.get('elasticsearch').get('timeout')
ELASTICSEARCH_RETRY_ON_TIMEOUT = RUN_CONFIG.get('elasticsearch').get('retry_on_timeout', False)

ES = elasticsearch.Elasticsearch(
    hosts=[{
        'host': ELASTICSEARCH_HOST,
        'port': ELASTICSEARCH_PORT,
        'transport_class': elasticsearch.Urllib3HttpConnection,
        'timeout': ELASTICSEARCH_TIMEOUT
    }],
    http_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
    retry_on_timeout=ELASTICSEARCH_RETRY_ON_TIMEOUT
)
