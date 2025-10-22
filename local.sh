#!/bin/bash
# ==============================================================================
# Local Development Server - WAAP Project
# ==============================================================================
# This script starts the Flask development server on your local machine.
#
# Usage:
#   ./local.sh
#
# The server will be accessible at:
#   http://127.0.0.1:8000
#
# Features:
#   - Debug mode enabled (auto-reload on code changes)
#   - Development environment settings
#   - Local-only access (127.0.0.1)
# ==============================================================================

# Set Flask environment to development mode
export FLASK_ENV=development

# Set project directory to current working directory
export PROJ_DIR=$PWD

# Enable debug mode for detailed error messages
export DEBUG=1

# Run our server locally with proper Python path
# - PYTHONPATH ensures Python can find all project modules
# - --debug enables auto-reload and detailed error pages
# - --host=127.0.0.1 restricts access to localhost only
# - --port=8000 sets the server port
PYTHONPATH=$(pwd):$PYTHONPATH
FLASK_APP=server.endpoints flask run --debug --host=127.0.0.1 --port=8000
