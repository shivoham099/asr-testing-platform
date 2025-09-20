#!/usr/bin/env python3
"""
Quick Start Script for ASR Testing Platform
Run this to get everything working in 2 minutes!
"""
import os
import sys
import subprocess
import webbrowser
import time

def print_banner():
    print("🚀" + "="*50 + "🚀")
    print("   ASR CROP TESTING PLATFORM - QUICK START")
    print("🚀" + "="*50 + "🚀")
    print()

def check_python():
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Please upgrade Python.")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
        return False

def create_directories():
    print("\n📁 Creating directories...")
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    print("✅ Directories created!")

def setup_google_oauth_quick():
    print("\n🔐 Google OAuth Setup (Quick Mode)")
    print("="*40)
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project")
    print("3. Enable Google+ API")
    print("4. Create OAuth 2.0 credentials")
    print("5. Add redirect URI: http://localhost:5000/login/authorized")
    print("6. Copy Client ID and Secret")
    
    # Open Google Cloud Console
    webbrowser.open("https://console.cloud.google.com/")
    
    print("\n⚠️  IMPORTANT: Update app.py with your credentials!")
    print("   Replace 'your-google-client-id' and 'your-google-client-secret'")
    
    input("\nPress Enter when you've updated app.py with your credentials...")

def start_server():
    print("\n🚀 Starting the server...")
    print("="*30)
    print("Server will start at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the Flask app
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    print_banner()
    
    # Check Python version
    if not check_python():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create directories
    create_directories()
    
    # Setup Google OAuth
    setup_google_oauth_quick()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
