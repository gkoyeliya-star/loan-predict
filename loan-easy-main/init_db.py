# init_db.py
from app_auth import app, db

def initialize_database():
    """
    Creates all database tables within the application context.
    This script is safe to run multiple times.
    """
    try:
        with app.app_context():
            print("Attempting to create database tables...")
            db.create_all()
            print("✓ Database tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"✗ An error occurred during database initialization: {e}")
        # Exit with a non-zero status code to fail the build if DB init fails
        import sys
        sys.exit(1)

if __name__ == "__main__":
    initialize_database()
