from flask import Flask, render_template
from flask_json import FlaskJSON
from config import config
from flask import g
from flask_cors import CORS
from flask_bootstrap import Bootstrap

json = FlaskJSON()
cors = CORS()
bootstrap = Bootstrap()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    json.init_app(app)
    cors.init_app(app)
    bootstrap.init_app(app)

    from .api_1_0 import api as api_1_0_bp
    app.register_blueprint(api_1_0_bp, url_prefix='/api/v1.0')

    from .wifi_views import wifi_views as wifi_views_bp
    app.register_blueprint(wifi_views_bp, url_prefix='/wifi')

    return app
