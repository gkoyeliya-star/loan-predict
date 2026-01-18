"""
WSGI entry point for the application server (e.g., Gunicorn).
"""
from app_auth import app

# Gunicorn looks for a variable named 'application' by default
application = app
