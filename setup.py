#!/usr/bin/env python3
"""
Quick setup script for ASR Testing Platform
"""
import os
import webbrowser
from urllib.parse import urlencode

def setup_google_oauth():
    print("🔐 Setting up Google OAuth...")
    print("\n1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable Google+ API")
    print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client IDs'")
    print("5. Application type: 'Web application'")
    print("6. Authorized redirect URIs: http://localhost:5000/login/authorized")
    print("7. Copy your Client ID and Client Secret")
    
    # Open Google Cloud Console
    webbrowser.open("https://console.cloud.google.com/")
    
    print("\n" + "="*50)
    print("Enter your Google OAuth credentials:")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    if client_id and client_secret:
        # Update app.py with credentials
        with open('app.py', 'r') as f:
            content = f.read()
        
        content = content.replace('your-google-client-id', client_id)
        content = content.replace('your-google-client-secret', client_secret)
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Google OAuth configured!")
        return True
    else:
        print("❌ Please enter valid credentials")
        return False

def setup_sarvam_api():
    print("\n🎤 Setting up Sarvam ASR API...")
    print("Enter your Sarvam API details:")
    
    api_endpoint = input("Sarvam API Endpoint URL: ").strip()
    api_key = input("API Key (if required): ").strip()
    
    if api_endpoint:
        # Update the mock function with real API call
        sarvam_code = f'''
def call_sarvam_asr(audio_data):
    """
    Sarvam ASR API integration
    """
    try:
        headers = {{'Content-Type': 'application/json'}}
        if '{api_key}':
            headers['Authorization'] = f'Bearer {api_key}'
        
        payload = {{
            'audio': audio_data,
            'language': 'hi',  # Hindi
            'format': 'wav'
        }}
        
        response = requests.post('{api_endpoint}', 
                               json=payload, 
                               headers=headers,
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('transcript', '').strip()
        else:
            print(f"Sarvam API error: {{response.status_code}} - {{response.text}}")
            return "API_ERROR"
            
    except Exception as e:
        print(f"Sarvam API exception: {{e}}")
        return "API_ERROR"
'''
        
        # Read and update app.py
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace the mock function
        start_marker = 'def call_sarvam_asr(audio_data):'
        end_marker = '    import random\n    return random.choice(mock_responses)'
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            new_content = content[:start_idx] + sarvam_code + content[end_idx:]
            
            with open('app.py', 'w') as f:
                f.write(new_content)
            
            print("✅ Sarvam API configured!")
            return True
    
    print("❌ Please enter valid API endpoint")
    return False

def install_dependencies():
    print("\n📦 Installing dependencies...")
    os.system("pip install -r requirements.txt")
    print("✅ Dependencies installed!")

def create_directories():
    print("\n📁 Creating directories...")
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    print("✅ Directories created!")

def main():
    print("🚀 ASR Testing Platform Setup")
    print("="*40)
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Setup Google OAuth
    oauth_success = setup_google_oauth()
    
    # Setup Sarvam API
    sarvam_success = setup_sarvam_api()
    
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETE!")
    print("="*50)
    
    if oauth_success and sarvam_success:
        print("✅ Everything configured!")
        print("\n🚀 To run the platform:")
        print("   python app.py")
        print("\n🌐 Then visit: http://localhost:5000")
    else:
        print("⚠️  Some setup incomplete, but you can still run:")
        print("   python app.py")
        print("\n📝 Update app.py manually with your credentials")

if __name__ == "__main__":
    main()
