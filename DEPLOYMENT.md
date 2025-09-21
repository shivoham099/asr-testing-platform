# 🚀 ASR Testing Platform - Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended - Free & Easy)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python app

3. **Set Environment Variables** (if needed)
   - Go to your project settings
   - Add any environment variables

4. **Your app will be live!**
   - Get your URL like: `https://your-app-name.railway.app`

### Option 2: Render (Free Tier)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose the repository

3. **Configure Service**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Option 3: Heroku (Free Tier Available)

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Or download from heroku.com
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-asr-platform-name
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

4. **Open Your App**
   ```bash
   heroku open
   ```

## 🔧 Pre-Deployment Setup

### 1. Initialize Git Repository
```bash
cd /Users/shivenderabrol/Downloads/asr-testing-platform
git init
git add .
git commit -m "Initial commit - ASR Testing Platform"
```

### 2. Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it: `asr-testing-platform`
4. Don't initialize with README (we already have files)
5. Click "Create repository"

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/asr-testing-platform.git
git branch -M main
git push -u origin main
```

## 🌐 After Deployment

### Your Platform Will Be Available At:
- **Railway**: `https://your-app-name.railway.app`
- **Render**: `https://your-app-name.onrender.com`
- **Heroku**: `https://your-app-name.herokuapp.com`

### Features Available:
- ✅ QA login system
- ✅ Multi-language support (Hindi, Odia, English, Gujarati, Malayalam)
- ✅ CSV upload for crop names
- ✅ Audio recording and ASR testing
- ✅ Results export as CSV
- ✅ Database storage

## 🔄 Making Updates

### Easy Update Process:
1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push origin main
   ```
3. Platform automatically redeploys with your changes!

## 🛠️ Troubleshooting

### Common Issues:
1. **Build Fails**: Check `requirements.txt` has all dependencies
2. **App Crashes**: Check logs in your hosting platform dashboard
3. **Database Issues**: The app creates SQLite database automatically

### Getting Help:
- Check platform-specific documentation
- Look at deployment logs in your hosting dashboard
- Most platforms have built-in monitoring and logs

## 💡 Pro Tips

1. **Start with Railway** - It's the easiest and most reliable
2. **Use GitHub** - Makes updates super easy
3. **Check Logs** - If something breaks, check the deployment logs
4. **Test Locally First** - Make sure everything works before deploying

## 🎉 You're All Set!

Once deployed, you can:
- Share the URL with your QA team
- Test ASR accuracy from anywhere
- Update the platform anytime by pushing to GitHub
- Scale up if you need more resources

Happy testing! 🎤✨

