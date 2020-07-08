"""
Element usage service
"""


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
    return {
        'operation_result': 'usage registered!'
    }
