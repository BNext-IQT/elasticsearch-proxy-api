"""
Schemas to validate the input of job status Endpoint
"""
from marshmallow import Schema, fields

class ESProxyQuery(Schema):
    """
    Class that the schema for getting a job status job by id
    """
    index_name = fields.String(required=True)
    es_query = fields.String(required=True)
    context_obj = fields.String()
    contextual_sort_data = fields.String()
