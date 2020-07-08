"""
Element usage service
"""
from datetime import datetime

from app.config import RUN_CONFIG
from app.usage_statistics import statistics_saver


class UsageRegistrationError(Exception):
    """
    Class for errors with the usage registration
    """


def register_element_usage(view_name, view_type, entity_name):
    """
    :param view_name: name of the view/element to register
    :param view_type: type of the element
    :param entity_name: name of the entity involved
    :return: result of the operation
    """
    index_name = RUN_CONFIG.get('usage_statistics').get('chembl_glados_es_view_record')
    document = {
        'view_name': view_name,
        'view_type': view_type,
        'entity_name': entity_name
        'run_env_type': RUN_CONFIG.get('run_env'),
        'request_date': datetime.utcnow().timestamp() * 1000,
        'host': 'es_proxy_api_k8s',
    }

    statistics_saver.save_record_to_elasticsearch(document, index_name)

    return {
        'operation_result': 'usage registered!'
    }
