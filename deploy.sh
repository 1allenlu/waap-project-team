#!/bin/bash
# ==============================================================================
# PythonAnywhere Deployment Script - WAAP Project
# ==============================================================================
# This shell script deploys a new version to the PythonAnywhere server.
#
# Prerequisites:
#   - sshpass must be installed (brew install sshpass on macOS)
#   - GEODATA2025_PA_PWD environment variable must be set with PythonAnywhere password
#
# Usage:
#   export GEODATA2025_PA_PWD="your-password-here"
#   ./deploy.sh
#
# What this script does:
#   1. Validates environment variables are set
#   2. SSH into PythonAnywhere server
#   3. Navigate to project directory
#   4. Execute rebuild.sh script on remote server
# ==============================================================================

# PythonAnywhere Configuration
PROJ_NAME=geodata2025

PROJ_DIR=$PROJ_NAME
VENV=$PROJ_NAME
PA_DOMAIN="$PROJ_NAME.pythonanywhere.com"
PA_USER=$PROJ_NAME

# Display deployment configuration
echo "===================================================================="
echo "PythonAnywhere Deployment Configuration"
echo "===================================================================="
echo "Project dir = $PROJ_DIR"
echo "PA domain = $PA_DOMAIN"
echo "Virtual env = $VENV"
echo "PA user = $PA_USER"

# Validate required environment variable
if [ -z "$GEODATA2025_PA_PWD" ]
then
    echo "ERROR: The PythonAnywhere password var (GEODATA2025_PA_PWD) must be set in the env."
    echo "Usage: export GEODATA2025_PA_PWD='your-password' && ./deploy.sh"
    exit 1
fi

echo "PA password = $GEODATA2025_PA_PWD"
echo "===================================================================="

# SSH into PythonAnywhere and execute rebuild script
# - sshpass: Provides password non-interactively for SSH
# - StrictHostKeyChecking no: Automatically accept SSH host key
# - EOF heredoc: Commands to execute on remote server
echo "SSHing to PythonAnywhere..."
# sshpass -p $GEODATA2025_PA_PWD ssh -o "StrictHostKeyChecking no" $PA_USER@ssh.pythonanywhere.com
sshpass -p $GEODATA2025_PA_PWD ssh -o "StrictHostKeyChecking no" $PA_USER@ssh.pythonanywhere.com << EOF
    cd ~/$PROJ_DIR; PA_USER=$PA_USER PROJ_DIR=~/$PROJ_DIR VENV=$VENV PA_DOMAIN=$PA_DOMAIN ./rebuild.sh
EOF

echo "===================================================================="
echo "Deployment complete!"
echo "===================================================================="
