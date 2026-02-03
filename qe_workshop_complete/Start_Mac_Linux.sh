#!/bin/bash
# =============================================================================
# Quantum ESPRESSO Workshop - Mac/Linux Startup Script
# =============================================================================
# This script starts the Docker container for the workshop.
# Prerequisites: Docker must be installed and running.
#
# Usage: ./Start_Mac_Linux.sh
# =============================================================================

echo ""
echo "============================================================"
echo "   Quantum ESPRESSO Workshop - Starting Environment"
echo "============================================================"
echo ""
echo "Please wait while the workshop environment starts..."
echo "(First run may take 5-10 minutes to download ~1GB of data)"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    echo ""
    echo "Please start Docker Desktop and wait for it to fully load."
    echo ""
    exit 1
fi

# Build and run the container
docker-compose up --build

echo ""
echo "Workshop environment stopped."
