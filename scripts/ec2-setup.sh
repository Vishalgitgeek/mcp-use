#!/bin/bash
# EC2 Setup Script for MCP Integration Service
# Run this on a fresh Ubuntu 22.04 EC2 instance

set -e

echo "========================================="
echo "MCP Integration Service - EC2 Setup"
echo "========================================="

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "[2/6] Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Git
echo "[3/6] Installing Git..."
sudo apt-get install -y git

# Clone repository
echo "[4/6] Cloning repository..."
cd ~
if [ -d "mcp-use" ]; then
    cd mcp-use
    git pull
else
    git clone https://github.com/Vishalgitgeek/mcp-use.git
    cd mcp-use
fi

# Create SSL directory
echo "[5/6] Setting up directories..."
mkdir -p nginx/ssl

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "[!] Creating .env file - PLEASE EDIT WITH YOUR VALUES!"
    cat > .env << 'EOF'
# Composio API Key (get from composio.dev)
COMPOSIO_API_KEY=your_composio_api_key_here

# Agent API Key (create a secure random string)
AGENT_API_KEY=your_secure_agent_api_key_here

# OAuth Redirect Base URL (use your EC2 public IP or domain)
OAUTH_REDIRECT_BASE=http://YOUR_EC2_PUBLIC_IP
EOF
    echo ""
    echo "========================================="
    echo "IMPORTANT: Edit .env file with your values!"
    echo "nano .env"
    echo "========================================="
fi

# Set permissions
chmod 600 .env

echo "[6/6] Setup complete!"
echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Start the services:"
echo "   docker compose up -d"
echo ""
echo "3. Check service status:"
echo "   docker compose ps"
echo "   docker compose logs -f app"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost/health"
echo ""
echo "5. Update Composio callback URL:"
echo "   Set callback to: http://YOUR_EC2_PUBLIC_IP/api/integrations/callback"
echo "========================================="
