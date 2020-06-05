"""
Schemas to validate the input of job status Endpoint
"""
from marshmallow import Schema, fields


class ESProxyQuery(Schema):
    """
    Class that the schema for getting es data
    """
    index_name = fields.String(required=True)
    es_query = fields.String(required=True)
    context_obj = fields.String()
    contextual_sort_data = fields.String()


class ESProxyDoc(Schema):
    """
    Class that the schema for getting a document by id
    """
    index_name = fields.String(required=True)
    doc_id = fields.String(required=True)
