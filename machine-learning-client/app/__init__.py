'''
Machine Learning Client Application
Provides API endpoints for audio transcription and voice cloning.
'''

from flask import Flask
from app.config import Config


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

    # Register blueprints
    from app.api.routes import api_bp

    app.register_blueprint(api_bp, url_prefix='/api')

    return app
