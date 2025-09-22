#!/usr/bin/env python3
"""
ASR Testing Platform for QA Testing - Supabase Version
A web-based platform for testing ASR accuracy with crop names using Supabase
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

# Import Supabase service
from supabase_service import (
    create_qa_user, create_test_session, get_test_session, 
    create_test_result, update_test_result, get_test_results,
    get_all_sessions, get_all_users
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

# Admin access - only specific Sarvam team members
ADMIN_EMAILS = [
    'shivesh@sarvam.ai',
    'prerna@sarvam.ai', 
    'shivender@sarvam.ai',
    'karman@sarvam.ai',
    'prajnavegesna@sarvam.ai'
]

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API configuration
SAARIKA_API_URL = "https://api.sarvam.ai/speech-to-text"
API_KEY = os.environ.get('SARVAM_API_KEY')

# Language code mappings
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

def is_admin(user_email):
    """Check if user has admin access"""
    return user_email in ADMIN_EMAILS

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
        
    try:
        # Create temporary file for input with optimized size
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            # Limit audio data size to prevent huge uploads (max 10MB)
            if len(audio_data) > 10 * 1024 * 1024:
                raise Exception("Audio file too large (max 10MB)")
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        # Convert to proper WAV format using ffmpeg
        converted_path = temp_path.replace('.webm', '.wav')
        
        # Use ffmpeg to convert to optimized 16kHz mono WAV with compression
        ffmpeg_cmd = [
            'ffmpeg', '-i', temp_path,
            '-ar', '16000',  # Sample rate 16kHz
            '-ac', '1',      # Mono
            '-acodec', 'pcm_s16le',  # 16-bit PCM for better compression
            '-f', 'wav',     # Force WAV format
            '-y',            # Overwrite output file
            converted_path
        ]
        
        process = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if process.returncode != 0:
            raise Exception(f"FFmpeg conversion failed: {process.stderr}")
        
        print(f"Using direct Sarvam API for transcription")
        print(f"Language: {language_code}")
        print(f"Model: {model_name}")
        print(f"Audio file: {converted_path}")
        
        # Use direct HTTP request with form data (as per API team specs)
        headers = {
            'api-subscription-key': API_KEY,
            'Connection': 'keep-alive',  # Reuse connections for faster requests
            'Accept-Encoding': 'gzip, deflate'  # Enable compression
        }
        
        # Prepare form data
        with open(converted_path, 'rb') as audio_file:
            files = {
                'file': ('audio.wav', audio_file, 'audio/wav')
            }
            data = {
                'model': model_name,
                'language_code': language_code
            }
            
            # Make API request with timeout and session for connection reuse
            session = requests.Session()
            session.headers.update(headers)
            
            # Set timeout to prevent hanging (30 seconds max)
            response = session.post(SAARIKA_API_URL, files=files, data=data, timeout=30)
        
        print(f"API Response status: {response.status_code}")
        print(f"API Response: {response.text}")
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        # Check if response is JSON
        try:
            response_data = response.json()
        except ValueError as e:
            # If response is not JSON (e.g., HTML error page), raise a more helpful error
            raise Exception(f"API returned non-JSON response (likely HTML error page): {response.text[:200]}...")
        
        if 'transcript' not in response_data:
            raise Exception(f"Invalid API response: {response_data}")
        
        return response_data
            
    except Exception as e:
        # Clean up temporary files if they exist
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
            if 'converted_path' in locals() and converted_path != temp_path:
                os.unlink(converted_path)
        except:
            pass
        raise Exception(f"Transcription failed: {str(e)}")

def check_keyword_match(transcript, crop_name):
    """
    Check if the crop name appears in the transcript
    
    Args:
        transcript (str): The transcribed text
        crop_name (str): The crop name to look for
        
    Returns:
        bool: True if crop name is found in transcript
    """
    if not transcript or not crop_name:
        return False
    
    # Convert to lowercase for case-insensitive matching
    transcript_lower = transcript.lower().strip()
    crop_name_lower = crop_name.lower().strip()
    
    # Check if crop name appears in transcript
    return crop_name_lower in transcript_lower

@app.route('/')
def index():
    """Home page - Google login"""
    if 'user' in session:
        return redirect(url_for('language_selection', user_id=session['user_id']))
    return render_template('index.html')

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    # Generate Google OAuth URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    return redirect(auth_url)

@app.route('/login/authorized')
def authorized():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    if not code:
        flash('Authorization failed', 'error')
        return redirect(url_for('index'))
    
    # Exchange code for token
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': GOOGLE_REDIRECT_URI
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Get user info
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Check if email domain is allowed
        email_domain = user_info['email'].split('@')[1]
        if email_domain not in ALLOWED_DOMAINS:
            flash('Access denied. Please use a Google account or Sarvam email.', 'error')
            return redirect(url_for('index'))
        
        # Create or get user in database
        user_id = create_qa_user(user_info['name'], user_info['email'])
        if not user_id:
            flash('Failed to create user account', 'error')
            return redirect(url_for('index'))
        
        # Store user info in session
        session['user'] = user_info
        session['user_id'] = user_id
        
        return redirect(url_for('language_selection', user_id=user_id))
        
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
        
        # Read CSV and extract crop names
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
        
        # Create test session
        session_id = create_test_session(user_id, language)
        if not session_id:
            flash('Failed to create test session', 'error')
            return redirect(url_for('upload_csv', user_id=user_id, language=language))
        
        # Store crop names in session for this session
        session[f'crops_{session_id}'] = crop_names
        
        # Clean up uploaded file
        os.unlink(filepath)
        
        # Redirect to testing page
        return redirect(url_for('testing', session_id=session_id, crop_index=0))
    
    flash('Invalid file type. Please upload a CSV file.', 'error')
    return redirect(url_for('upload_csv', user_id=user_id, language=language))

@app.route('/testing/<int:session_id>/<int:crop_index>')
def testing(session_id, crop_index):
    """Testing page for recording audio"""
    # Get session info
    session_info = get_test_session(session_id)
    if not session_info:
        flash('Session not found', 'error')
        return redirect(url_for('index'))
    
    # Get language from session info
    language = session_info['language']
    
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
    total_crops = len(crops)
    
    return render_template('testing.html', 
                         session_id=session_id,
                         crop_index=crop_index,
                         current_crop=current_crop,
                         total_crops=total_crops,
                         qa_name=session_info['qa_users']['name'],
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
        # Get session info for language
        session_info = get_test_session(session_id)
        if not session_info:
            return jsonify({'error': 'Session not found'}), 400
        
        language = session_info['language']
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Transcribe audio
        transcription_result = transcribe_audio(audio_data, language)
        
        if 'transcript' not in transcription_result:
            return jsonify({'error': 'No transcript in API response'}), 400
        
        transcript = transcription_result['transcript']
        
        # Check keyword match
        keyword_detected = check_keyword_match(transcript, crop_name)
        
        # Update result in database
        success = update_test_result(session_id, crop_name, attempt_number, transcript, keyword_detected)
        
        if not success:
            return jsonify({'error': 'Failed to save result'}), 500
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'keyword_detected': keyword_detected
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in submit_recording: {error_msg}")
        
        # Provide more specific error messages
        if "API returned non-JSON response" in error_msg:
            return jsonify({'error': 'Server error: API returned HTML instead of JSON. Please try again.'}), 500
        elif "SARVAM_API_KEY environment variable not set" in error_msg:
            return jsonify({'error': 'Server configuration error: API key not set'}), 500
        elif "FFmpeg conversion failed" in error_msg:
            return jsonify({'error': 'Audio processing error: Unable to convert audio format'}), 500
        else:
            return jsonify({'error': f'Recording submission failed: {error_msg}'}), 500

@app.route('/results/<int:session_id>')
def results(session_id):
    """Display test results"""
    # Get session info
    session_info = get_test_session(session_id)
    if not session_info:
        flash('Session not found', 'error')
        return redirect(url_for('index'))
    
    # Get test results
    results_data = get_test_results(session_id)
    
    if not results_data:
        return render_template('results.html', 
                             session_id=session_id,
                             qa_name=session_info['qa_users']['name'],
                             language=session_info['language'],
                             created_at=datetime.fromisoformat(session_info['created_at'].replace('Z', '+00:00')),
                             results=[],
                             well_pronounced_count=0,
                             moderate_count=0,
                             poor_count=0)
    
    # Process results
    processed_results = []
    well_pronounced_count = 0
    moderate_count = 0
    poor_count = 0
    
    for result in results_data:
        crop_name = result['crop_name']
        logs = []
        correct_count = result['correct_attempts']
        
        for i in range(1, 6):
            sentence = result.get(f'log_{i}_sentence', '')
            detected = result.get(f'log_{i}_keyword_detected', False)
            logs.append({'sentence': sentence, 'detected': detected})
        
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
            'total_attempts': 5,
            'result_ratio': f"{correct_count}/5",
            'logs': logs
        })
    
    return render_template('results.html', 
                         session_id=session_id,
                         qa_name=session_info['qa_users']['name'],
                         language=session_info['language'],
                         created_at=datetime.fromisoformat(session_info['created_at'].replace('Z', '+00:00')),
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
    """Download results as CSV"""
    # Get session info
    session_info = get_test_session(session_id)
    if not session_info:
        flash('Session not found', 'error')
        return redirect(url_for('index'))
    
    # Get test results
    results_data = get_test_results(session_id)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['QA Name', 'Crop Name', 'Language', 'Overall Result']
    for i in range(1, 6):
        header.extend([f'Log {i} Output', f'Log {i} Keyword Detected'])
    writer.writerow(header)
    
    # Write data
    for result in results_data:
        crop_name = result['crop_name']
        correct_count = result['correct_attempts']
        
        row = [session_info['qa_users']['name'], crop_name, session_info['language'], f"{correct_count}/5"]
        
        for i in range(1, 6):
            sentence = result.get(f'log_{i}_sentence', '')
            detected = result.get(f'log_{i}_keyword_detected', False)
            row.extend([sentence, detected])
        
        writer.writerow(row)
    
    # Get CSV content
    csv_content = output.getvalue()
    output.close()
    
    # Create file-like object
    csv_file = io.BytesIO()
    csv_file.write(csv_content.encode('utf-8'))
    csv_file.seek(0)
    
    return send_file(
        csv_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'asr_test_results_{session_info["qa_users"]["name"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/qa_guide')
def qa_guide():
    """QA Workflow Guide"""
    return render_template('qa_workflow_guide.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)

