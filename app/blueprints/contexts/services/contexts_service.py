"""
Context Service
"""
from app.context_loader import context_loader


class ContextError(Exception):
    """
    Class for errors in this module
    """


def get_context_data(context_dict):
    """
    :param context_dict: dict describing the context
    :return: the data for the context given as parameter
    """
    try:
        context_data, total_items = context_loader.get_context(context_dict)
        return {
            'context_data': context_data,
            'total_items': total_items
        }
    except context_loader.ContextLoaderError as error:
        raise ConnectionError(repr(error))
