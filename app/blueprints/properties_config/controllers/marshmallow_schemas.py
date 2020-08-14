"""
Marshmallow schemas for validating the properties configuration controller
"""
from marshmallow import Schema, fields


class PropertyConfigRequest(Schema):
    """
    Class with the schema for getting the configuration of a property
    """
    index_name = fields.String(required=True)
    property_id = fields.String(required=True)


class GroupConfigRequest(Schema):
    """
    Class with the schema for getting the configuration of a group
    """
    index_name = fields.String(required=True)
    group_name = fields.String(required=True)


class FacetsGroupConfigRequest(Schema):
    """
    Class with the schema for getting the configuration of a facet group
    """
    index_name = fields.String(required=True)
    group_name = fields.String(required=True)


class IDPropertiesRequest(Schema):
    """
    Class with the schema for getting the id properties of an index
    """
    index_name = fields.String(required=True)

class AllPropertiesRequest(Schema):
    """
    Class with the schema for getting all the properties config of an index
    """
    index_name = fields.String(required=True)
