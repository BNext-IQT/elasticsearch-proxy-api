"""
Module that handles the connection with the elasticsearch used for monitoring
"""
import elasticsearch
from app.config import RUN_CONFIG

ES_MONITORING_CONFIG = RUN_CONFIG.get('usage_statistics', {}).get('elasticsearch')

ELASTICSEARCH_HOST = ES_MONITORING_CONFIG.get('host')
ELASTICSEARCH_PORT = ES_MONITORING_CONFIG.get('port')
ELASTICSEARCH_USERNAME = ES_MONITORING_CONFIG.get('username')
ELASTICSEARCH_PASSWORD = ES_MONITORING_CONFIG.get('password')
ELASTICSEARCH_TIMEOUT = ES_MONITORING_CONFIG.get('timeout', 30)
ELASTICSEARCH_RETRY_ON_TIMEOUT = ES_MONITORING_CONFIG.get('retry_on_timeout', True)

ES_MONITORING = elasticsearch.Elasticsearch(
    hosts=[{
        'host': ELASTICSEARCH_HOST,
        'port': ELASTICSEARCH_PORT,
        'transport_class': elasticsearch.Urllib3HttpConnection,
        'timeout': ELASTICSEARCH_TIMEOUT
    }],
    http_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
    retry_on_timeout=ELASTICSEARCH_RETRY_ON_TIMEOUT
)
