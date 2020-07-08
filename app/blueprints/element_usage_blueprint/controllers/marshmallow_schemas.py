"""
Marshmallow schemas for validating the frontend element usage registration
"""
from marshmallow import Schema, fields


class RegisterUsageRequest(Schema):
    """
    Class with the schema for registering the usage of an element
    """
    view_name = fields.String(required=True)
    view_type = fields.String(required=True)
    entity_name = fields.String(required=True)
