#!/bin/bash
# provision.sh — Linux system setup script for storage infrastructure nodes
# Usage: bash scripts/provision.sh

set -e

echo "============================================"
echo " Distributed Storage Infrastructure Setup"
echo "============================================"

# Update system packages
echo "[1/6] Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

# Install Docker
echo "[2/6] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed successfully."
else
    echo "Docker already installed: $(docker --version)"
fi

# Install Docker Compose
echo "[3/6] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed: $(docker-compose --version)"
else
    echo "Docker Compose already installed."
fi

# Install Python 3.10+
echo "[4/6] Installing Python 3.10..."
sudo apt-get install -y python3.10 python3.10-venv python3-pip

# Set up Python virtual environment
echo "[5/6] Setting up Python virtual environment..."
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Python environment ready."

# Set up environment file
echo "[6/6] Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created. Please update with your actual credentials."
else
    echo ".env already exists."
fi

echo ""
echo "============================================"
echo " Setup Complete!"
echo " Run: docker-compose up --build"
echo " API Docs: http://localhost:8000/docs"
echo " Prometheus: http://localhost:9090"
echo "============================================"
