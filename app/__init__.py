import os
import logging
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

def create_app(test_config=None):
    """Application factory function"""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        GROQ_API_KEY=os.getenv('GROQ_API_KEY')
    )

    # Load environment variables
    if test_config is None:
        app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
        # Debug logging
        if app.config['GROQ_API_KEY']:
            app.logger.info('Groq API key loaded successfully')
        else:
            app.logger.error('GROQ_API_KEY environment variable is not set!')
            raise RuntimeError('Groq API key not found in environment variables!')
    else:
        # Load test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register routes
    from app import routes
    app.register_blueprint(routes.bp)

    return app
