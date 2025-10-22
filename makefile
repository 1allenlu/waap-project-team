# ==============================================================================
# WAAP Project Team - Main Makefile
# ==============================================================================
# This makefile orchestrates builds, tests, and deployments for the WAAP
# (Web Application and API Protection) project.
#
# Common targets:
#   make dev_env    - Set up development environment with dependencies
#   make all_tests  - Run all test suites across all modules
#   make prod       - Run tests and push to GitHub (production workflow)
#   make github     - Commit and push changes to master branch
#   make docs       - Generate project documentation
# ==============================================================================

# Include common makefile definitions and shared variables
include common.mk

# Set Python path to project root for proper module imports
export PYTHONPATH := $(shell pwd)

# ==============================================================================
# Directory Structure Configuration
# ==============================================================================
# Our directories - centralized location references
CITIES_DIR = cities          # City-level data and queries module
DB_DIR = data                # Database and data storage
REQ_DIR = .                  # Requirements files location (project root)
SEC_DIR = security           # Security utilities and validation
SERVER_DIR = server          # Server and API implementation

# ==============================================================================
# Phony Targets
# ==============================================================================
# FORCE: Utility target to force execution of dependent targets
# This ensures targets always run regardless of file timestamps
FORCE:

# ==============================================================================
# Production Deployment Workflow
# ==============================================================================
# prod: Complete production deployment pipeline
# Runs all tests to ensure code quality, then pushes to GitHub
prod: all_tests github

# ==============================================================================
# Version Control Operations
# ==============================================================================
# github: Commit all changes and push to master branch
# The '-' prefix on git commit allows the command to fail gracefully
# (useful when there are no changes to commit)
github: FORCE
	- git commit -a
	git push origin master

# ==============================================================================
# Testing
# ==============================================================================
# all_tests: Run comprehensive test suite across all project modules
# Executes tests in: cities, security, and server modules
# Each module's tests are defined in their respective makefiles
all_tests: FORCE
	cd $(CITIES_DIR); make tests
	cd $(SEC_DIR); make tests
	cd $(SERVER_DIR); make tests

# ==============================================================================
# Development Environment Setup
# ==============================================================================
# dev_env: Set up local development environment
# Installs all development dependencies and displays PYTHONPATH configuration
# Run this first when setting up the project on a new machine
dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt
	@echo "PYTHONPATH is automatically set to: "
	@echo $(shell pwd)

# ==============================================================================
# Documentation Generation
# ==============================================================================
# docs: Generate project documentation
# Builds documentation from source code and docstrings
docs: FORCE
	cd $(API_DIR); make docs