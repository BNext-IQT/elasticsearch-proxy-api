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