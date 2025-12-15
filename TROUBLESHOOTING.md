# Troubleshooting Guide

## OAuth Authentication Issues

### Error: "Could not retrieve user email: Request is missing required authentication credential"

**Cause:** The OAuth scopes don't include userinfo scopes needed to get the user's email.

**Solution:**
1. **Update OAuth Consent Screen Scopes:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to **APIs & Services** → **OAuth consent screen**
   - Click **"Edit App"**
   - Go to **"Scopes"** tab
   - Click **"Add or Remove Scopes"**
   - Add these scopes if not already present:
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
   - Click **"Update"** → **"Save and Continue"**

2. **Re-authorize the Application:**
   - Since you previously authorized with only Drive scope, you need to re-authorize
   - Delete any existing tokens in the `tokens/` directory (or just the specific user's token file)
   - Click **"+ Add Account"** again
   - You'll see a new consent screen asking for additional permissions
   - Grant all requested permissions

3. **Verify Scopes in Code:**
   - The code should now include all three scopes (already fixed in `config.py`):
     - Drive scope
     - Userinfo email scope
     - Userinfo profile scope

### Error: "Access blocked: This app request is invalid"

See [OAUTH_SETUP.md](OAUTH_SETUP.md) for complete setup instructions.

### Error: "redirect_uri_mismatch"

**Solution:**
- In Google Cloud Console → Credentials → Your OAuth Client
- Make sure these redirect URIs are added:
  - `http://localhost:8000/auth/callback`
  - `http://127.0.0.1:8000/auth/callback`
- The URI must match **exactly** (including http vs https, port number, etc.)

### Error: "App is in testing mode"

**Solution:**
- Add your email to "Test users" in OAuth consent screen
- OR publish the app (for production use)

### After Fixing Scopes, Still Getting Errors

1. **Clear existing tokens:**
   ```bash
   # Delete all token files
   rm -rf tokens/*.json
   # Or on Windows:
   del tokens\*.json
   ```

2. **Re-run OAuth flow:**
   - Click "+ Add Account" again
   - You should see the updated consent screen with all scopes

3. **Check server logs:**
   - Look for detailed error messages in the terminal where server is running

## General Issues

### Server Won't Start

- Make sure virtual environment is activated
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Import Errors

- Activate virtual environment: `.\venv\Scripts\Activate.ps1` (PowerShell) or `venv\Scripts\activate.bat` (CMD)
- Install dependencies: `pip install -r requirements.txt`

### MCP Server Errors

- Check if Node.js is installed: `node --version`
- Verify npx is available: `npx --version`
- Some MCP servers may need additional setup

