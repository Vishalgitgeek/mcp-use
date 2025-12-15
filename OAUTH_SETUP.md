# Google OAuth Setup Guide

## "Access blocked: This app request is invalid" Error

This error occurs when Google OAuth is not properly configured. Follow these steps:

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name (e.g., "Local Drive Sync")
4. Click **"Create"**

## Step 2: Enable Google Drive API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Drive API"**
3. Click on it and press **"Enable"**

## Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Choose **"External"** (unless you have a Google Workspace)
3. Click **"Create"**
4. Fill in the required fields:
   - **App name**: Local Drive Sync (or any name)
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **"Save and Continue"**
6. On **"Scopes"** page, click **"Add or Remove Scopes"**
   - Search for and add these scopes:
     - `https://www.googleapis.com/auth/drive` (for Drive access)
     - `https://www.googleapis.com/auth/userinfo.email` (to get user email)
     - `https://www.googleapis.com/auth/userinfo.profile` (to get user profile)
   - Click **"Update"** → **"Save and Continue"**
7. On **"Test users"** page (if app is in Testing mode):
   - Click **"Add Users"**
   - Add your email address
   - Click **"Save and Continue"**
8. Review and **"Back to Dashboard"**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, configure consent screen (follow Step 3)
4. Choose **"Web application"** as application type
5. Give it a name (e.g., "Local Drive Sync Client")
6. **Authorized redirect URIs**: Add:
   ```
   http://localhost:8000/auth/callback
   http://127.0.0.1:8000/auth/callback
   ```
7. Click **"Create"**
8. **IMPORTANT**: Copy the **Client ID** and **Client Secret**

## Step 5: Configure .env File

Create or edit `.env` file in your project root:

```env
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
OPENAI_API_KEY=your_openai_api_key_here
```

**Replace:**
- `your_client_id_here.apps.googleusercontent.com` with your actual Client ID
- `your_client_secret_here` with your actual Client Secret

## Step 6: Common Issues & Solutions

### Issue 1: "Access blocked: This app request is invalid"
**Causes:**
- Client ID/Secret not set in `.env`
- Redirect URI mismatch
- OAuth consent screen not configured

**Solutions:**
1. Verify `.env` file exists and has correct values
2. Check redirect URI matches exactly: `http://localhost:8000/auth/callback`
3. Make sure OAuth consent screen is published or you're added as test user

### Issue 2: "redirect_uri_mismatch"
**Solution:**
- In Google Cloud Console → Credentials → Your OAuth Client
- Add both:
  - `http://localhost:8000/auth/callback`
  - `http://127.0.0.1:8000/auth/callback`

### Issue 3: "App is in testing mode"
**Solution:**
- Add your email to "Test users" in OAuth consent screen
- OR publish the app (not recommended for personal use)

### Issue 4: "Invalid client"
**Solution:**
- Double-check Client ID and Secret in `.env`
- Make sure there are no extra spaces or quotes
- Restart the server after changing `.env`

## Step 7: Verify Configuration

Run this to check if environment variables are loaded:

```python
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
print(f"Client ID: {GOOGLE_CLIENT_ID[:20]}..." if GOOGLE_CLIENT_ID else "NOT SET")
print(f"Client Secret: {'SET' if GOOGLE_CLIENT_SECRET else 'NOT SET'}")
```

## Quick Checklist

- [ ] Google Cloud project created
- [ ] Google Drive API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth 2.0 Client ID created (Web application)
- [ ] Redirect URI added: `http://localhost:8000/auth/callback`
- [ ] `.env` file created with Client ID and Secret
- [ ] Server restarted after `.env` changes
- [ ] Your email added as test user (if app in testing mode)

## Testing

1. Start server: `python server.py`
2. Open: `http://localhost:8000`
3. Click **"+ Add Account"**
4. You should see Google sign-in page
5. After authorizing, you'll be redirected back

If you still see errors, check the server terminal for detailed error messages.

