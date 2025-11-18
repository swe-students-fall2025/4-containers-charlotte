'''
Machine Learning Client Application
Provides API endpoints for audio transcription and voice cloning.
'''

from flask import Flask
from app.config import Config
from app.api import routes


def create_app(config_class=Config):
    '''
    Application factory pattern for Flask app.

    Parameters
    ----------
    config_class : class, default=Config
        Configuration class to use.

    Returns
    -------
    app : Flask
        Configured Flask application instance.
    '''
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize directories
    config_class.init_directories()

    # Register blueprints
    app.register_blueprint(routes.api_bp, url_prefix='/api')

    return app
