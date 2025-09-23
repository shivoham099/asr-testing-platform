#!/usr/bin/env python3
"""
ASR Testing Platform for QA Testing - Azure Version
A web-based platform for testing ASR accuracy with crop names using Azure Blob Storage
"""

import os
import json
import csv
import tempfile
import subprocess
import soundfile as sf
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import requests
import io

# Import Azure service
from azure_service import (
    upload_asr_test_results
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Google OAuth Configuration
app.config['GOOGLE_ID'] = os.environ.get('GOOGLE_ID', 'your-google-client-id')
app.config['GOOGLE_SECRET'] = os.environ.get('GOOGLE_SECRET', 'your-google-client-secret')

# Google OAuth Configuration
GOOGLE_CLIENT_ID = app.config['GOOGLE_ID']
GOOGLE_CLIENT_SECRET = app.config['GOOGLE_SECRET']
GOOGLE_REDIRECT_URI = 'https://asr-testing-platform.onrender.com/login/authorized'

# Allowed email domains (All Google accounts + Sarvam team)
ALLOWED_DOMAINS = ['gmail.com', 'googlemail.com', 'google.com', 'sarvam.ai']  # Allow all Google accounts + Sarvam

# Sarvam API Configuration
API_KEY = os.environ.get('SARVAM_API_KEY')
SAARIKA_API_URL = "https://api.sarvam.ai/speech-to-text"
model_name = "saarika:v2.5"

# Language codes for Sarvam API
BCP47_CODES = {
    "hindi": "hi-IN", 
    "malayalam": "ml-IN",
    "gujarati": "gu-IN",
    "odia": "or-IN",
    "english": "en-IN",
    "punjabi": "pa-IN"
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_audio(audio_data, language, model_name="saarika:v2.5"):
    """
    Transcribe audio using Sarvam API (direct HTTP request as per API team specs)
    
    Args:
        audio_data (bytes): Raw audio data
        language (str): Language of the audio
        model_name (str): Model version to use (saarika:v2.5, saarika:v2, saarika:v1, saarika:flash)
        
    Returns:
        dict: Response containing transcription and metadata
    """
    if not API_KEY:
        raise ValueError("SARVAM_API_KEY environment variable not set")
        
        if language not in BCP47_CODES:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(BCP47_CODES.keys())}")
        
        # Get language code
        language_code = BCP47_CODES[language]
        
    # Prepare request data as per API team specifications
    files = {
        'audio': ('audio.wav', audio_data, 'audio/wav')
    }
    
    data = {
        'model': model_name,
        'language': language_code
    }
    
    headers = {
        'api-subscription-key': API_KEY
    }
    
    try:
        # Make request to Sarvam API
        response = requests.post(
            SAARIKA_API_URL,
            files=files,
            data=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'transcript': result.get('transcript', ''),
                'confidence': result.get('confidence', 0.0),
                'language': result.get('language', language_code),
                'model': result.get('model', model_name)
            }
        else:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {response.text}"
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        raise Exception("API request timed out")
    except requests.exceptions.ConnectionError:
        raise Exception("Failed to connect to API server")
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

def check_keyword_match(transcript, crop_name):
    """Check if crop name is detected in transcript"""
    transcript_lower = transcript.lower().strip()
    crop_lower = crop_name.lower().strip()
    
    # Direct match
    if crop_lower in transcript_lower:
        return True
    
    # Check for partial matches (useful for compound words)
    crop_words = crop_lower.split()
    transcript_words = transcript_lower.split()
    
    # If crop name has multiple words, check if all words are present
    if len(crop_words) > 1:
        return all(word in transcript_lower for word in crop_words)
    
    # For single words, check if it's a substring
    return crop_lower in transcript_lower

@app.route('/')
def index():
    """Login page"""
    return render_template('index.html', 
                         google_client_id=GOOGLE_CLIENT_ID,
                         redirect_uri=GOOGLE_REDIRECT_URI)

@app.route('/login/authorized')
def login_authorized():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code
        code = request.args.get('code')
        app.logger.info(f"DEBUG: Received code: {code[:20]}..." if code else "DEBUG: No code received")
        if not code:
            app.logger.error("DEBUG: No authorization code received")
            flash('Authorization failed', 'error')
            return redirect(url_for('index'))
        
        # Exchange code for access token
        app.logger.info(f"DEBUG: Client ID: {GOOGLE_CLIENT_ID}")
        app.logger.info(f"DEBUG: Client Secret: {GOOGLE_CLIENT_SECRET[:10]}..." if GOOGLE_CLIENT_SECRET else "DEBUG: No client secret")
        app.logger.info(f"DEBUG: Redirect URI: {GOOGLE_REDIRECT_URI}")
        
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        app.logger.info(f"DEBUG: Making token request to: {token_url}")
        token_response = requests.post(token_url, data=token_data)
        app.logger.info(f"DEBUG: Token response status: {token_response.status_code}")
        app.logger.info(f"DEBUG: Token response: {token_response.text}")
        
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            app.logger.error(f"DEBUG: No access token in response: {token_json}")
            flash('Failed to get access token', 'error')
            return redirect(url_for('index'))
        
        access_token = token_json['access_token']
        
        # Get user info from Google
        user_info_url = f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}'
        user_response = requests.get(user_info_url)
        user_info = user_response.json()
        
        if 'email' not in user_info:
            flash('Failed to get user information', 'error')
            return redirect(url_for('index'))
        
        # Check email domain
        email_domain = user_info['email'].split('@')[1]
        if email_domain not in ALLOWED_DOMAINS:
            flash('Access denied. Please use a Google account or Sarvam email.', 'error')
            return redirect(url_for('index'))
        
        # Store user info in session (session-based storage)
        session['user'] = user_info
        session['user_id'] = int(datetime.now().strftime('%Y%m%d%H%M%S'))
        
        return redirect(url_for('language_selection', user_id=session['user_id']))
            
    except Exception as e:
        flash(f'Login failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/language_selection/<int:user_id>')
def language_selection(user_id):
    """Language selection page"""
    if 'user' not in session or session['user_id'] != user_id:
        flash('Please log in first', 'error')
        return redirect(url_for('index'))
    
    languages = ['hindi', 'malayalam', 'gujarati', 'odia', 'english', 'punjabi']
    return render_template('language_selection.html', user_id=user_id, languages=languages)

@app.route('/upload_csv/<int:user_id>')
def upload_csv(user_id):
    """CSV upload page"""
    if 'user' not in session or session['user_id'] != user_id:
        flash('Please log in first', 'error')
        return redirect(url_for('index'))

    language = request.args.get('language', 'hindi')
    return render_template('upload_csv.html', user_id=user_id, language=language)

@app.route('/process_csv', methods=['POST'])
def process_csv():
    """Process uploaded CSV file"""
    user_id = request.form.get('user_id')
    language = request.form.get('language')
    
    if 'csv_file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('upload_csv', user_id=user_id, language=language))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_csv', user_id=user_id, language=language))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read CSV file
        crop_names = []
        try:
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and row[0].strip():  # Skip empty rows
                        crop_names.append(row[0].strip())
        except Exception as e:
            flash(f'Error reading CSV file: {str(e)}', 'error')
            return redirect(url_for('upload_csv', user_id=user_id, language=language))
        
        if not crop_names:
            flash('No crop names found in CSV file', 'error')
            return redirect(url_for('upload_csv', user_id=user_id, language=language))
        
        # Create test session (generate unique session ID)
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store language and crop names in session for this session
        session['current_language'] = language
        session[f'crops_{session_id}'] = crop_names
        
        # Clean up uploaded file
        os.unlink(filepath)
        
        # Redirect to testing page
        return redirect(url_for('testing', session_id=session_id, crop_index=0))
    
    flash('Invalid file type. Please upload a CSV file.', 'error')
    return redirect(url_for('upload_csv', user_id=user_id, language=language))

@app.route('/testing/<session_id>/<int:crop_index>')
def testing(session_id, crop_index):
    """Testing page for recording audio"""
    # Get session info from Flask session
    if f'crops_{session_id}' not in session:
        flash('Session not found', 'error')
        return redirect(url_for('index'))
    
    # Get language from session
    language = session.get('current_language', 'hindi')
    
    # Get crop names from session (uploaded CSV) or use sample crops
    uploaded_crops = session.get(f'crops_{session_id}', [])
    
    if uploaded_crops:
        # Use uploaded crop names
        crops = uploaded_crops
    else:
        # Fallback to sample crops
        from sample_crops_data import get_sample_crops
        crops = get_sample_crops(language)
    
    if not crops or crop_index >= len(crops):
        flash('No more crops to test', 'error')
        return redirect(url_for('results', session_id=session_id))
    
    current_crop = crops[crop_index]
    next_crop_index = crop_index + 1 if crop_index + 1 < len(crops) else None
    
    return render_template('testing.html', 
                         session_id=session_id,
                         crop_index=crop_index,
                         current_crop=current_crop,
                         next_crop_index=next_crop_index,
                         total_crops=len(crops),
                         language=language)

@app.route('/submit_recording', methods=['POST'])
def submit_recording():
    """Handle audio recording submission"""
    session_id = request.form.get('session_id')
    crop_name = request.form.get('crop_name')
    attempt_number = int(request.form.get('attempt_number', 1))
    
    # Get audio file
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file received'}), 400
    
    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400
    
    try:
        # Get language from session
        language = session.get('current_language', 'hindi')
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Transcribe audio
        transcription_result = transcribe_audio(audio_data, language)
        
        if 'transcript' not in transcription_result:
            return jsonify({'error': 'No transcript in API response'}), 400
        
        transcript = transcription_result['transcript']
        
        # Check keyword match
        keyword_detected = check_keyword_match(transcript, crop_name)
        
        # Store result in session
        if f'results_{session_id}' not in session:
            session[f'results_{session_id}'] = []
        
        result = {
            'crop_name': crop_name,
            'attempt_number': attempt_number,
            'transcript': transcript,
            'keyword_detected': keyword_detected,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        session[f'results_{session_id}'].append(result)
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'keyword_detected': keyword_detected
        })
        
    except Exception as e:
        error_msg = str(e)
        if "FFmpeg conversion failed" in error_msg:
            return jsonify({'error': 'Audio processing error: Unable to convert audio format'}), 500
        else:
            return jsonify({'error': f'Recording submission failed: {error_msg}'}), 500

@app.route('/results/<int:session_id>')
def results(session_id):
    """Display test results"""
    # Get results from session
    results_data = session.get(f'results_{session_id}', [])
    
    if not results_data:
        return render_template('results.html', 
                             session_id=session_id,
                             qa_name=session.get('user', {}).get('name', 'Unknown'),
                             language=session.get('current_language', 'hindi'),
                             created_at=datetime.now(),
                             results=[],
                             well_pronounced_count=0,
                             moderate_count=0,
                             poor_count=0)
    
    # Process results - group by crop name
    crop_results = {}
    for result in results_data:
        crop_name = result['crop_name']
        if crop_name not in crop_results:
            crop_results[crop_name] = []
        crop_results[crop_name].append(result)
    
    # Process each crop's results
    processed_results = []
    well_pronounced_count = 0
    moderate_count = 0
    poor_count = 0
    
    for crop_name, attempts in crop_results.items():
        correct_count = sum(1 for attempt in attempts if attempt['keyword_detected'])
        total_attempts = len(attempts)
        
        # Create logs for display
        logs = []
        for attempt in attempts:
            logs.append({
                'sentence': attempt['transcript'],
                'detected': attempt['keyword_detected']
            })
        
        # Count by performance level
        if correct_count >= 3:
            well_pronounced_count += 1
        elif correct_count == 2:
            moderate_count += 1
        else:
            poor_count += 1
        
        processed_results.append({
            'crop_name': crop_name,
            'correct_count': correct_count,
            'total_attempts': total_attempts,
            'result_ratio': f"{correct_count}/{total_attempts}",
            'logs': logs
        })
    
    return render_template('results.html', 
                         session_id=session_id,
                         qa_name=session.get('user', {}).get('name', 'Unknown'),
                         language=session.get('current_language', 'hindi'),
                         created_at=datetime.now(),
                         results=processed_results,
                         well_pronounced_count=well_pronounced_count,
                         moderate_count=moderate_count,
                         poor_count=poor_count)

@app.route('/end_session/<int:session_id>')
def end_session(session_id):
    """End testing session and redirect to results"""
    return redirect(url_for('results', session_id=session_id))

@app.route('/download_csv/<int:session_id>')
def download_csv(session_id):
    """Download results as CSV and upload to Azure"""
    # Get results from session
    results_data = session.get(f'results_{session_id}', [])
    
    if not results_data:
        flash('No results found for this session', 'error')
        return redirect(url_for('index'))
    
    try:
        # Upload results to Azure
        user_email = session.get('user', {}).get('email', 'unknown@example.com')
        language = session.get('current_language', 'hindi')
        
        azure_url = upload_asr_test_results(
            test_results=results_data,
            user_email=user_email,
            language=language,
            session_id=str(session_id)
        )
        
        flash(f'Results uploaded to Azure successfully! URL: {azure_url}', 'success')
        return redirect(url_for('results', session_id=session_id))
        
    except Exception as e:
        flash(f'Failed to upload results to Azure: {str(e)}', 'error')
        return redirect(url_for('results', session_id=session_id))

@app.route('/qa_guide')
def qa_guide():
    """QA Workflow Guide"""
    return render_template('qa_workflow_guide.html')

@app.route('/csv_format_guide')
def csv_format_guide():
    """CSV Format Guide"""
    return render_template('csv_format_guide.html')

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

