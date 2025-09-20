# 🔐 Google OAuth Setup Guide

## Step 1: Create Google OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project** (or select existing)
   - Click "New Project"
   - Name: "ASR Testing Platform"
   - Click "Create"

3. **Enable Google+ API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Name: "ASR Testing Platform"

5. **Configure Authorized URLs**
   - **Authorized JavaScript origins:**
     - `https://asr-testing-platform.onrender.com`
     - `http://localhost:5000` (for local testing)
   
   - **Authorized redirect URIs:**
     - `https://asr-testing-platform.onrender.com/login/authorized`
     - `http://localhost:5000/login/authorized` (for local testing)

6. **Get Your Credentials**
   - Copy the **Client ID** and **Client Secret**

## Step 2: Set Environment Variables on Render

1. **Go to your Render dashboard**
2. **Select your service**
3. **Go to "Environment" tab**
4. **Add these environment variables:**
   - `GOOGLE_ID`: Your Google Client ID
   - `GOOGLE_SECRET`: Your Google Client Secret

## Step 3: Update Allowed Domains

In `app.py`, update the `ALLOWED_DOMAINS` list:

```python
ALLOWED_DOMAINS = ['sarvam.ai', 'gmail.com']  # Add your team domains
```

## Step 4: Deploy the Updated Code

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add Google OAuth authentication"
   git push origin main
   ```

2. **Render will automatically redeploy**

## Step 5: Test the Authentication

1. **Visit your live URL**
2. **Click "Sign in with Google"**
3. **Use a Sarvam team email**
4. **Verify access is granted**

## 🔒 Security Features

- ✅ **Domain restriction**: Only @sarvam.ai emails can access
- ✅ **Google OAuth**: Secure authentication
- ✅ **Session management**: Automatic logout
- ✅ **User tracking**: All actions logged with user info

## 🛠️ Troubleshooting

### Common Issues:

1. **"Access denied" error**
   - Check if email domain is in `ALLOWED_DOMAINS`
   - Verify Google OAuth credentials

2. **"Invalid redirect URI"**
   - Check authorized redirect URIs in Google Console
   - Ensure URL matches exactly

3. **"Client ID not found"**
   - Verify environment variables are set on Render
   - Check for typos in variable names

## 📧 Support

If you need help, check:
- Google OAuth documentation
- Render environment variables guide
- Flask-OAuthlib documentation
