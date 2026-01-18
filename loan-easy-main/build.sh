#!/bin/bash

# Exit on error
set -o errexit

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt

echo "--- Initializing the database ---"
python init_db.py

echo "--- Build complete ---"
