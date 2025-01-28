from flask import Flask
from flask_cors import CORS
from config.config import MAX_CONTENT_LENGTH
import os

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
    
    # Enable CORS
    CORS(app)
    
    # Configure max content length
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Register blueprints
    from app.routes.main_routes import main
    app.register_blueprint(main)
    
    return app 