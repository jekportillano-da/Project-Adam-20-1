import os
from app import create_app

# Create Flask application instance
app = create_app()

if __name__ == "__main__":
    # Get port and host from environment or use defaults
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Run the application
    app.run(host=host, port=port)