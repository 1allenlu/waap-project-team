# ==============================================================================
# WAAP Project Team - Main Makefile
# ==============================================================================
# This makefile orchestrates builds, tests, and deployments for the WAAP
# (Web Application and API Protection) project.
#
# Common targets:
#   make help       - Display this help message (default target)
#   make dev_env    - Set up development environment with dependencies
#   make all_tests  - Run all test suites across all modules
#   make prod       - Run tests and push to GitHub (production workflow)
#   make github     - Commit and push changes to master branch
#   make docs       - Generate project documentation
#
# Usage examples:
#   make dev_env                    # First-time setup
#   make all_tests                  # Run tests before committing
#   make prod                       # Deploy to production
# ==============================================================================

# Default target - show help when running 'make' with no arguments
.DEFAULT_GOAL := help

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
# Declare phony targets to avoid conflicts with files of the same name
# and ensure they always execute even if a file with that name exists
.PHONY: help prod github all_tests dev_env docs clean FORCE

# FORCE: Utility target to force execution of dependent targets
# This ensures targets always run regardless of file timestamps
FORCE:

# ==============================================================================
# Help Target
# ==============================================================================
# help: Display available make targets with descriptions
# This is the default target when you run 'make' with no arguments
help:
	@echo "===================================================================="
	@echo "WAAP Project Team - Available Make Targets"
	@echo "===================================================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev_env    - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make all_tests  - Run all test suites (cities, security, server)"
	@echo ""
	@echo "Deployment:"
	@echo "  make prod       - Run tests and push to GitHub (full pipeline)"
	@echo "  make github     - Commit all changes and push to master"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs       - Generate project documentation"
	@echo ""
	@echo "Utility:"
	@echo "  make clean      - Remove temporary files and caches"
	@echo "  make help       - Display this help message"
	@echo ""
	@echo "===================================================================="
	@echo "Current PYTHONPATH: $(PYTHONPATH)"
	@echo "===================================================================="

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
	pip install -r $(CURDIR)/requirements-dev.txt
	@echo "PYTHONPATH is automatically set to: "
	@echo $(shell pwd)

# ==============================================================================
# Documentation Generation
# ==============================================================================
# docs: Generate project documentation
# Builds documentation from source code and docstrings
docs: FORCE
	cd $(API_DIR); make docs

# ==============================================================================
# Cleanup
# ==============================================================================
# clean: Remove temporary files, Python cache, and build artifacts
# Useful for ensuring a fresh build or freeing up disk space
clean: FORCE
	@echo "Cleaning up temporary files and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "Cleanup complete!"

# ==============================================================================
# Additional Notes
# ==============================================================================
# - All targets use FORCE dependency to ensure they run every time
# - The PYTHONPATH is automatically set to the project root for all commands
# - Test failures will stop the 'prod' target from pushing to GitHub
# - The '-' prefix on 'git commit' allows it to fail if there's nothing to commit
# ==============================================================================