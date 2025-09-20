#!/usr/bin/env python3
"""
Test script for Sarvam ASR API integration
"""

import os
import json
import subprocess
import tempfile
import soundfile as sf
import numpy as np

# API configuration
SAARIKA_API_URL = "https://api.sarvam.ai/speech-to-text"
API_KEY = 'sk_b5ytcz77_i95Ys6RPGfu2LrK3F2xgydU4'

# Language code mappings
BCP47_CODES = {
    "hindi": "hi-IN",
    "odia": "od-IN", 
    "english": "en-IN",
    "gujarati": "gu-IN",
    "malayalam": "ml-IN"
}

def create_test_audio(duration=3, sample_rate=16000):
    """Create a simple test audio file with a sine wave"""
    # Generate a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440  # A4 note
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.1  # Low volume
    
    return audio_data, sample_rate

def test_asr_api(language="hindi"):
    """Test the ASR API with a simple audio file"""
    
    if language not in BCP47_CODES:
        print(f"Unsupported language: {language}")
        return False
    
    language_code = BCP47_CODES[language]
    
    try:
        # Create test audio
        print(f"Creating test audio for {language}...")
        audio_data, sample_rate = create_test_audio()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            sf.write(temp_file.name, audio_data, sample_rate, format='wav')
            audio_path = temp_file.name
        
        print(f"Test audio saved to: {audio_path}")
        
        # Construct curl command
        curl_cmd = [
            'curl', '--location', SAARIKA_API_URL,
            '--header', f'api-subscription-key: {API_KEY}',
            '--form', f'file=@{audio_path};type=audio/wav',
            '--form', f'model=saarika:v2.5',
            '--form', f'language_code={language_code}'
        ]
        
        print("Sending request to Sarvam API...")
        print(f"Language: {language} ({language_code})")
        
        # Execute curl command
        process = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        os.unlink(audio_path)
        
        if process.returncode != 0:
            print(f"API request failed: {process.stderr}")
            return False
        
        # Parse response
        try:
            response_data = json.loads(process.stdout)
            print("API Response:")
            print(json.dumps(response_data, indent=2))
            return True
        except json.JSONDecodeError:
            print(f"Invalid JSON response: {process.stdout}")
            return False
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

def main():
    """Test ASR API for all supported languages"""
    print("Testing Sarvam ASR API Integration")
    print("=" * 50)
    
    languages = ["hindi", "odia", "english", "gujarati", "malayalam"]
    
    for language in languages:
        print(f"\nTesting {language.upper()}...")
        success = test_asr_api(language)
        if success:
            print(f"✅ {language} test passed")
        else:
            print(f"❌ {language} test failed")
        print("-" * 30)
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
