"""
Entry file for the elasticsearch proxy app
"""

from flask import Flask
from flask_cors import CORS

from app.config import RUN_CONFIG
from app.cache import CACHE
from app.blueprints.swagger_description.swagger_description_blueprint import SWAGGER_BLUEPRINT
from app.blueprints.es_proxy.controllers.es_proxy_controller import ES_PROXY_BLUEPRINT
from app.blueprints.properties_config.controllers.properties_config_controller import PROPERTIES_CONFIG_BLUEPRINT
from app.blueprints.contexts.controllers.contexts_controller import CONTEXTS_BLUEPRINT
from app.blueprints.search_parser.controllers.search_parser_controller import SEARCH_PARSER_BLUEPRINT
from app.blueprints.url_shortening.controllers.url_shortening_controller import URL_SHORTENING_BLUEPRINT
from app.blueprints.element_usage_blueprint.controllers.element_usage_controller import ELEMENT_USAGE_BLUEPRINT


def create_app():
    """
    Creates the flask app
    :return: Elasticsearch proxy flask app
    """
    base_path = RUN_CONFIG.get('base_path')
    flask_app = Flask(__name__)

    enable_cors = RUN_CONFIG.get('enable_cors', False)

    if enable_cors:
        CORS(flask_app)

    with flask_app.app_context():
        CACHE.init_app(flask_app)

        # pylint: disable=protected-access
        if RUN_CONFIG.get('cache_config').get('CACHE_TYPE') == 'memcached':
            CACHE.cache._client.behaviors['tcp_nodelay'] = True
            CACHE.cache._client.behaviors['_noreply'] = True
            CACHE.cache._client.behaviors['no_block'] = True
            CACHE.cache._client.behaviors['remove_failed'] = 10
            CACHE.cache._client.behaviors['retry_timeout'] = 10
            CACHE.cache._client.behaviors['retry_timeout'] = 600

    flask_app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=f'{base_path}/swagger')
    flask_app.register_blueprint(ES_PROXY_BLUEPRINT, url_prefix=f'{base_path}/es_data')
    flask_app.register_blueprint(PROPERTIES_CONFIG_BLUEPRINT, url_prefix=f'{base_path}/properties_configuration')
    flask_app.register_blueprint(CONTEXTS_BLUEPRINT, url_prefix=f'{base_path}/contexts')
    flask_app.register_blueprint(SEARCH_PARSER_BLUEPRINT, url_prefix=f'{base_path}/search_parsing')
    flask_app.register_blueprint(URL_SHORTENING_BLUEPRINT, url_prefix=f'{base_path}/url_shortening')
    flask_app.register_blueprint(ELEMENT_USAGE_BLUEPRINT, url_prefix=f'{base_path}/frontend_element_usage')

    return flask_app


if __name__ == '__main__':
    FLASK_APP = create_app()
