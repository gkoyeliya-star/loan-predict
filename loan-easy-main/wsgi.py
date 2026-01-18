"""
WSGI entry point for the application server (e.g., Gunicorn).
"""
from app_auth import app

# Gunicorn looks for a variable named 'application' by default
application = app

if __name__ == "__main__":
    # This block is for local development and won't be executed by Gunicorn
    app.run()
