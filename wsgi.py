"""
WSGI config for the Elasticsearch API server.
"""
from app import create_app

FLASK_APP = create_app()
