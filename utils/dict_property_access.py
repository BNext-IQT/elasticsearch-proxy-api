"""
Module with helper functions for accessing dictionary properties
"""


def get_property_value(obj, str_property, default_null_value=None):
    """
    :param obj:
    :param str_property: string path of the property, e.g  '_metadata.assay_data.assay_subcellular_fraction'
    :param default_null_value: value to return when the value in the dict is None. For example, it can return '' if indicated
    :return: the value of a property (separated by dots) in a dict. such as  '_metadata.assay_data.assay_subcellular_fraction'

    """

    prop_parts = str_property.split('.')
    current_prop = prop_parts[0]
    if len(prop_parts) > 1:
        current_obj = obj.get(current_prop)
        if current_obj is None:
            return default_null_value
        else:
            return get_property_value(current_obj, '.'.join(prop_parts[1::]))
    else:

        value = obj.get(current_prop)
        value = default_null_value if value is None else value
        return value
