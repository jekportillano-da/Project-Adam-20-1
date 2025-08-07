from flask import Flask
import os

def create_app(test_config=None):
    app = Flask(__name__,
              static_folder='../static',
              template_folder='../templates')
    app.config.from_mapping(SECRET_KEY='dev')
    
    if test_config is not None:
        app.config.update(test_config)

    from app import routes
    app.register_blueprint(routes.bp, url_prefix='/')

    return app
