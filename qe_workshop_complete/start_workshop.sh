#!/bin/bash
# =============================================================================
# Quantum ESPRESSO Workshop Launcher — Linux / macOS
# =============================================================================
# Usage: bash start_workshop.sh
# =============================================================================

echo "=========================================================="
echo "  QUANTUM ESPRESSO WORKSHOP ENVIRONMENT"
echo "=========================================================="
echo ""

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH."
    echo ""
    echo "Install Docker:"
    echo "  Linux:  See DOCKER_SETUP_GUIDE.md (Step 1)"
    echo "  macOS:  Download Docker Desktop from https://docker.com"
    echo ""
    exit 1
fi

# Check Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker is installed but the daemon is not running."
    echo ""
    echo "  Linux:  sudo systemctl start docker"
    echo "  macOS:  Open Docker Desktop from Applications"
    echo ""
    exit 1
fi

# Check if image exists locally
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "indranilm/qe-workshop:latest"; then
    echo "Workshop image not found locally. Downloading..."
    echo "(This may take 20-40 minutes on the first run)"
    echo ""
    docker pull indranilm/qe-workshop:latest
    echo ""
fi

# Stop any existing container with the same name
docker stop qe-workshop 2>/dev/null
docker rm qe-workshop 2>/dev/null

echo "Starting workshop environment..."
echo ""
echo "──────────────────────────────────────────────────────────"
echo "  Open your browser and go to: http://localhost:8888"
echo "  Navigate to: notebooks_enhanced/"
echo "  To stop: press Ctrl+C in this terminal"
echo "──────────────────────────────────────────────────────────"
echo ""

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker run -it --rm \
  --name qe-workshop \
  -p 8888:8888 \
  -v "${SCRIPT_DIR}":/workspace \
  -e OMPI_ALLOW_RUN_AS_ROOT=1 \
  -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
  indranilm/qe-workshop:latest
