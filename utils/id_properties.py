"""
Module that helps loading values from an id property list
"""
def get_id_value(id_properties_list, item: dict):
    """
    :param id_properties_list: the properties that identify the item
    :param item: the item for which to get the id value
    :return: the value that identifies the item
    """
    id_values = [str(item.get(id_property)) for id_property in id_properties_list]

    return '-'.join(id_values)