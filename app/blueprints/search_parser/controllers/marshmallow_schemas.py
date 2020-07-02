"""
Marshmallow schemas for validating the queries to the search parser
"""
from marshmallow import Schema, fields


class ParseFreeTextSearchRequest(Schema):
    """
    Class with the schema for parsing a free text search
    """
    search_term = fields.String(required=True)
    es_indexes = fields.String(required=True)
    selected_es_index = fields.String()
