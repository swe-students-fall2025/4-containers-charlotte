'''
Machine Learning Client Application
Provides API endpoints for audio transcription and voice cloning.
'''

from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprints
    from app.api.routes import api_bp

    app.register_blueprint(api_bp, url_prefix='/api')

    return app
