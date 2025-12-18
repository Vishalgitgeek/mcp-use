# MCP Integration Service - Deployment Guide

## Prerequisites

- AWS Account
- Domain name (for OAuth)
- Google Cloud Console project with OAuth configured
- Composio account with API key

## Step 1: Launch EC2 Instance

### AWS Console Steps:

1. Go to **EC2 → Launch Instance**
2. Configure:
   - **Name:** `mcp-integration-service`
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance type:** `t2.small` (minimum) or `t2.medium`
   - **Key pair:** Create new or use existing
   - **Network settings:**
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere
     - Allow HTTPS (port 443) from anywhere
   - **Storage:** 20 GB gp3

3. Click **Launch Instance**
4. Note the **Public IP** address

## Step 2: Configure DNS

1. Go to your DNS provider
2. Add an **A Record**:
   - **Name:** `mcp` (or your preferred subdomain)
   - **Value:** Your EC2 Public IP
   - **TTL:** 300

3. Wait 5-10 minutes for DNS propagation
4. Verify: `ping mcp.yourdomain.com`

## Step 3: Connect to EC2

```bash
# Replace with your key file and EC2 IP
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

## Step 4: Run Setup Script

```bash
# Clone or copy your code to the server
cd ~
git clone https://github.com/your-repo/mcp-use.git
# OR use scp to copy files

# Run setup script
cd mcp-use
chmod +x deploy/setup.sh
./deploy/setup.sh
```

## Step 5: Deploy Application

```bash
# Copy code to /opt/mcp-service
sudo cp -r ~/mcp-use/* /opt/mcp-service/
cd /opt/mcp-service

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create production .env
cp deploy/.env.production .env
nano .env  # Edit with your actual values
```

## Step 6: Configure Nginx

```bash
# Copy nginx config
sudo cp deploy/nginx.conf /etc/nginx/sites-available/mcp-service

# Edit and replace YOUR_DOMAIN with actual domain
sudo nano /etc/nginx/sites-available/mcp-service

# Enable site
sudo ln -s /etc/nginx/sites-available/mcp-service /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Step 7: Get SSL Certificate

```bash
# Get certificate from Let's Encrypt
sudo certbot --nginx -d mcp.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect option (2)
```

## Step 8: Start Service

```bash
# Copy systemd service file
sudo cp deploy/mcp-service.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable mcp-service

# Start service
sudo systemctl start mcp-service

# Check status
sudo systemctl status mcp-service
```

## Step 9: Update OAuth Settings

### Google Cloud Console:

1. Go to **APIs & Services → Credentials**
2. Edit your OAuth 2.0 Client ID
3. Add **Authorized redirect URIs:**
   ```
   https://mcp.yourdomain.com/auth/callback
   ```
4. Save

### Composio Dashboard:

1. Go to your Composio app settings
2. Update callback URL to:
   ```
   https://mcp.yourdomain.com/api/integrations/callback
   ```

## Step 10: Verify Deployment

```bash
# Check service is running
sudo systemctl status mcp-service

# Check logs
sudo journalctl -u mcp-service -f

# Test health endpoint
curl https://mcp.yourdomain.com/api/tools/health

# Test from browser
# Visit: https://mcp.yourdomain.com
```

---

## Useful Commands

### Service Management

```bash
# Start/Stop/Restart
sudo systemctl start mcp-service
sudo systemctl stop mcp-service
sudo systemctl restart mcp-service

# View logs
sudo journalctl -u mcp-service -f
sudo journalctl -u mcp-service --since "1 hour ago"

# Check status
sudo systemctl status mcp-service
```

### Nginx

```bash
# Test config
sudo nginx -t

# Reload (apply config changes)
sudo systemctl reload nginx

# View logs
sudo tail -f /var/log/nginx/mcp-service.error.log
sudo tail -f /var/log/nginx/mcp-service.access.log
```

### SSL Certificate Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

### MongoDB (if local)

```bash
# Start/Stop
sudo systemctl start mongod
sudo systemctl stop mongod

# Check status
sudo systemctl status mongod

# Connect to shell
mongosh
```

---

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u mcp-service -n 50

# Common issues:
# - Missing .env file
# - Wrong Python path
# - Port already in use
```

### 502 Bad Gateway

```bash
# Check if service is running
sudo systemctl status mcp-service

# Check if port 8001 is listening
sudo netstat -tlnp | grep 8001
```

### OAuth not working

1. Check redirect URIs match exactly in Google Console
2. Ensure OAUTH_REDIRECT_BASE in .env uses https://
3. Verify SSL certificate is valid

### DNS not resolving

```bash
# Check DNS propagation
dig mcp.yourdomain.com

# Wait longer or try different DNS
nslookup mcp.yourdomain.com 8.8.8.8
```

---

## Security Checklist

- [ ] Change default AGENT_API_KEY to secure random value
- [ ] Change JWT_SECRET to secure random value
- [ ] Enable firewall (ufw)
- [ ] Disable SSH password authentication
- [ ] Set up fail2ban
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`
- [ ] Set up MongoDB authentication (if local)
- [ ] Regular backups of MongoDB
