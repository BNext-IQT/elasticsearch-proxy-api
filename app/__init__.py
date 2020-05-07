"""
Entry file for the elasticsearch proxy app
"""

from flask import Flask

from app.config import RUN_CONFIG
from app.cache import CACHE
from app.blueprints.swagger_description.swagger_description_blueprint import SWAGGER_BLUEPRINT


def create_app():
    """
    Creates the flask app
    :return: Elasticsearch proxy flask app
    """
    base_path = RUN_CONFIG.get('base_path')
    flask_app = Flask(__name__)

    with flask_app.app_context():
        CACHE.init_app(flask_app)

    flask_app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=f'{base_path}/swagger')

    return flask_app

if __name__ == '__main__':
    FLASK_APP = create_app()
