"""
Marshmallow schemas for validating the properties configuration controller
"""
from marshmallow import Schema, fields


class ContextDataRequest(Schema):
    """
    Class with the schema for getting the data of a context
    """
    context_type = fields.String(required=True)
    context_id = fields.String(required=True)
    delayed_jobs_base_url = fields.String(required=True)
