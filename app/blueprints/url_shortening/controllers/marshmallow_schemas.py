"""
Marshmallow schemas for validating the url shortening controller
"""
from marshmallow import Schema, fields


class ShortenURLRequest(Schema):
    """
    Class with the schema for shortening a URL
    """
    long_url = fields.String(required=True)


class ExpandURLRequest(Schema):
    """
    Class with the schema for shortening a URL
    """
    url_hash = fields.String(required=True)
