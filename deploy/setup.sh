#!/bin/bash
# MCP Integration Service - EC2 Setup Script
# Run this on a fresh Ubuntu 22.04 EC2 instance

set -e  # Exit on error

echo "=========================================="
echo "MCP Integration Service - EC2 Setup"
echo "=========================================="

# Update system
echo "[1/8] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
echo "[2/8] Installing Python 3.11..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install Nginx
echo "[3/8] Installing Nginx..."
sudo apt install -y nginx

# Install Certbot for SSL
echo "[4/8] Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Install MongoDB (optional - skip if using Atlas)
echo "[5/8] Installing MongoDB..."
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Create app directory
echo "[6/8] Setting up application directory..."
sudo mkdir -p /opt/mcp-service
sudo chown $USER:$USER /opt/mcp-service

# Create virtual environment
echo "[7/8] Creating Python virtual environment..."
cd /opt/mcp-service
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies (run after copying code)
echo "[8/8] Setup complete!"
echo ""
echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo "1. Copy your code to /opt/mcp-service/"
echo "2. Copy .env.production to /opt/mcp-service/.env"
echo "3. Run: cd /opt/mcp-service && source venv/bin/activate && pip install -r requirements.txt"
echo "4. Copy nginx config: sudo cp deploy/nginx.conf /etc/nginx/sites-available/mcp-service"
echo "5. Enable nginx site: sudo ln -s /etc/nginx/sites-available/mcp-service /etc/nginx/sites-enabled/"
echo "6. Remove default: sudo rm /etc/nginx/sites-enabled/default"
echo "7. Copy systemd service: sudo cp deploy/mcp-service.service /etc/systemd/system/"
echo "8. Enable service: sudo systemctl enable mcp-service"
echo "9. Get SSL cert: sudo certbot --nginx -d YOUR_DOMAIN"
echo "10. Start service: sudo systemctl start mcp-service"
echo "=========================================="
