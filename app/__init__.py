"""
Entry file for the elasticsearch proxy app
"""
from flask import Flask

from app.config import RUN_CONFIG
from app.cache import CACHE


def create_app():
    """
    Creates the flask app
    :return: Elasticsearch proxy flask app
    """
    # base_path = RUN_CONFIG.get('base_path')

    flask_app = Flask(__name__)

    with flask_app.app_context():
        CACHE.init_app(flask_app)

    return flask_app

if __name__ == '__main__':
    flask_app = create_app()
