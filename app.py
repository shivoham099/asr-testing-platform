#!/usr/bin/env python3
"""
ASR Testing Platform for QA Testing
A web-based platform for testing ASR accuracy with crop names
"""

import os
import json
import csv
import sqlite3
import tempfile
import subprocess
import soundfile as sf
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import requests
import io

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

# Allowed email domains (All Google accounts for now)
ALLOWED_DOMAINS = ['gmail.com', 'googlemail.com', 'google.com']  # Allow all Google accounts

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

# Database setup
def init_db():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect('asr_testing.db')
    cursor = conn.cursor()
    
    # Create QA users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create test sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qa_user_id INTEGER,
            language TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (qa_user_id) REFERENCES qa_users (id)
        )
    ''')
    
    # Create test results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            crop_name TEXT NOT NULL,
            total_attempts INTEGER DEFAULT 5,
            correct_attempts INTEGER DEFAULT 0,
            result_ratio TEXT,
            log_1_sentence TEXT,
            log_1_keyword_detected BOOLEAN,
            log_2_sentence TEXT,
            log_2_keyword_detected BOOLEAN,
            log_3_sentence TEXT,
            log_3_keyword_detected BOOLEAN,
            log_4_sentence TEXT,
            log_4_keyword_detected BOOLEAN,
            log_5_sentence TEXT,
            log_5_keyword_detected BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES test_sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_allowed_user(email):
    """Check if user email is from allowed domain"""
    if not email:
        return False
    domain = email.split('@')[-1].lower()
    return domain in ALLOWED_DOMAINS

@google.tokengetter
def get_google_oauth_token():
    """Get Google OAuth token from session"""
    return session.get('google_token')

def transcribe_audio(audio_data, language="hindi", model_name="saarika:v2.5"):
    """
    Transcribe audio data using Sarvam API
    
    Args:
        audio_data (bytes): Audio data in WAV format
        language (str): Language of the audio
        model_name (str): Model version to use
        
    Returns:
        dict: Response containing transcription and metadata
    """
    
    if language not in BCP47_CODES:
        raise ValueError(f"Unsupported language: {language}. Supported: {list(BCP47_CODES.keys())}")
    
    # Get language code
    language_code = BCP47_CODES[language]
    
    try:
        # Create temporary file for input
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        # Convert to proper WAV format using ffmpeg
        converted_path = temp_path.replace('.webm', '.wav')
        
        # Use ffmpeg to convert to 16kHz mono WAV
        ffmpeg_cmd = [
            'ffmpeg', '-i', temp_path,
            '-ar', '16000',  # Sample rate 16kHz
            '-ac', '1',      # Mono
            '-y',            # Overwrite output file
            converted_path
        ]
        
        # Execute ffmpeg conversion
        ffmpeg_process = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if ffmpeg_process.returncode != 0:
            # If ffmpeg fails, try with soundfile directly
            try:
                # Try to read with soundfile
                audio_data_array, sampling_rate = sf.read(temp_path)
                
                # Convert to 16kHz mono WAV
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as converted_file:
                    sf.write(converted_file.name, audio_data_array, 16000, format='wav', subtype='PCM_16')
                    converted_path = converted_file.name
            except Exception as sf_error:
                raise Exception(f"Audio conversion failed: {str(sf_error)}")
        
        # Construct curl command
        curl_cmd = [
            'curl', '--location', SAARIKA_API_URL,
            '--header', f'api-subscription-key: {API_KEY}',
            '--form', f'file=@{converted_path};type=audio/wav',
            '--form', f'model={model_name}',
            '--form', f'language_code={language_code}'
        ]
        
        # Execute curl command
        process = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Clean up temporary files
        try:
            os.unlink(temp_path)
            if converted_path != temp_path:
                os.unlink(converted_path)
        except:
            pass
        
        if process.returncode != 0:
            raise Exception(f"API request failed: {process.stderr}")
        
        # Parse response
        try:
            response_data = json.loads(process.stdout)
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {process.stdout}")
        
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

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('google_token', None)
    session.pop('user', None)
    session.pop('user_id', None)
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from callback
        code = request.args.get('code')
        if not code:
            flash('Authorization failed: No code received', 'error')
            return redirect(url_for('index'))
        
        # Exchange code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            flash('Failed to get access token', 'error')
            return redirect(url_for('index'))
        
        access_token = token_json['access_token']
        
        # Get user info
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_info = user_response.json()
        
        email = user_info.get('email', '')
        name = user_info.get('name', '')
        
        # Check if user is from allowed domain
        if not is_allowed_user(email):
            flash(f'Access denied. Only Google accounts can access this platform. Your email: {email}', 'error')
            return redirect(url_for('index'))
        
        # Store or get QA user
        conn = sqlite3.connect('asr_testing.db')
        cursor = conn.cursor()
        
        # Check if user exists, if not create
        cursor.execute('SELECT id FROM qa_users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute('INSERT INTO qa_users (name, email) VALUES (?, ?)', (name, email))
            user_id = cursor.lastrowid
        else:
            user_id = user[0]
            # Update name in case it changed
            cursor.execute('UPDATE qa_users SET name = ? WHERE email = ?', (name, email))
        
        conn.commit()
        conn.close()
        
        # Store user info in session
        session['user'] = {
            'name': name,
            'email': email
        }
        session['user_id'] = user_id
        
        flash(f'Welcome, {name}!', 'success')
        return redirect(url_for('language_selection', user_id=user_id))
        
    except Exception as e:
        flash(f'Login failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/language_selection/<int:user_id>')
def language_selection(user_id):
    """Language selection page"""
    return render_template('language_selection.html', user_id=user_id, languages=BCP47_CODES.keys())

@app.route('/upload_csv/<int:user_id>/<language>')
def upload_csv(user_id, language):
    """CSV upload page"""
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
        conn = sqlite3.connect('asr_testing.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO test_sessions (qa_user_id, language) VALUES (?, ?)', (user_id, language))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return redirect(url_for('testing', session_id=session_id, crop_index=0))
    
    flash('Invalid file type. Please upload a CSV file.', 'error')
    return redirect(url_for('upload_csv', user_id=user_id, language=language))

@app.route('/testing/<int:session_id>/<int:crop_index>')
def testing(session_id, crop_index):
    """Testing page for recording audio"""
    # Get session info and crop names
    conn = sqlite3.connect('asr_testing.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ts.language, qu.name 
        FROM test_sessions ts 
        JOIN qa_users qu ON ts.qa_user_id = qu.id 
        WHERE ts.id = ?
    ''', (session_id,))
    
    session_info = cursor.fetchone()
    if not session_info:
        flash('Session not found', 'error')
        return redirect(url_for('index'))
    
    language, qa_name = session_info
    
    # For now, we'll use sample crop names. In production, this would come from the uploaded CSV
    sample_crops = [
        "गेहूं", "चावल", "मक्का", "बाजरा", "ज्वार", "रागी", "अरहर", "चना", "मूंग", "उड़द"
    ]
    
    if crop_index >= len(sample_crops):
        # All crops tested, show results
        return redirect(url_for('results', session_id=session_id))
    
    current_crop = sample_crops[crop_index]
    
    conn.close()
    
    return render_template('testing.html', 
                         session_id=session_id, 
                         crop_index=crop_index,
                         current_crop=current_crop,
                         language=language,
                         qa_name=qa_name,
                         total_crops=len(sample_crops))

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
        # Read audio data
        audio_data = audio_file.read()
        
        # Get session language
        conn = sqlite3.connect('asr_testing.db')
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM test_sessions WHERE id = ?', (session_id,))
        session = cursor.fetchone()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 400
        
        language = session[0]
        
        # Transcribe audio
        transcription_result = transcribe_audio(audio_data, language)
        
        if 'transcript' not in transcription_result:
            return jsonify({'error': 'No transcript in API response'}), 400
        
        transcript = transcription_result['transcript']
        
        # Check keyword match
        keyword_detected = check_keyword_match(transcript, crop_name)
        
        # Store result in database
        cursor.execute('''
            SELECT id FROM test_results 
            WHERE session_id = ? AND crop_name = ?
        ''', (session_id, crop_name))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing record
            result_id = result[0]
            cursor.execute(f'''
                UPDATE test_results 
                SET log_{attempt_number}_sentence = ?, 
                    log_{attempt_number}_keyword_detected = ?
                WHERE id = ?
            ''', (transcript, keyword_detected, result_id))
        else:
            # Create new record
            cursor.execute('''
                INSERT INTO test_results (session_id, crop_name, log_1_sentence, log_1_keyword_detected)
                VALUES (?, ?, ?, ?)
            ''', (session_id, crop_name, transcript, keyword_detected))
            result_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'keyword_detected': keyword_detected,
            'result_id': result_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<int:session_id>')
def results(session_id):
    """Display test results"""
    conn = sqlite3.connect('asr_testing.db')
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute('''
        SELECT ts.language, qu.name, ts.created_at
        FROM test_sessions ts 
        JOIN qa_users qu ON ts.qa_user_id = qu.id 
        WHERE ts.id = ?
    ''', (session_id,))
    
    session_info = cursor.fetchone()
    if not session_info:
        flash('Session not found', 'error')
        return redirect(url_for('index'))
    
    language, qa_name, created_at = session_info
    
    # Get test results
    cursor.execute('''
        SELECT crop_name, log_1_sentence, log_1_keyword_detected,
               log_2_sentence, log_2_keyword_detected,
               log_3_sentence, log_3_keyword_detected,
               log_4_sentence, log_4_keyword_detected,
               log_5_sentence, log_5_keyword_detected
        FROM test_results 
        WHERE session_id = ?
        ORDER BY id
    ''', (session_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # Process results
    processed_results = []
    for result in results:
        crop_name = result[0]
        logs = []
        correct_count = 0
        
        for i in range(1, 11, 2):  # Check each log pair (sentence, keyword_detected)
            sentence = result[i] if result[i] else ""
            detected = result[i+1] if result[i+1] is not None else False
            logs.append({'sentence': sentence, 'detected': detected})
            if detected:
                correct_count += 1
        
        processed_results.append({
            'crop_name': crop_name,
            'correct_count': correct_count,
            'total_attempts': 5,
            'result_ratio': f"{correct_count}/5",
            'logs': logs
        })
    
    return render_template('results.html', 
                         session_id=session_id,
                         qa_name=qa_name,
                         language=language,
                         results=processed_results,
                         created_at=created_at)

@app.route('/download_csv/<int:session_id>')
def download_csv(session_id):
    """Download results as CSV"""
    conn = sqlite3.connect('asr_testing.db')
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute('''
        SELECT qu.name, ts.language
        FROM test_sessions ts 
        JOIN qa_users qu ON ts.qa_user_id = qu.id 
        WHERE ts.id = ?
    ''', (session_id,))
    
    session_info = cursor.fetchone()
    if not session_info:
        return "Session not found", 404
    
    qa_name, language = session_info
    
    # Get test results
    cursor.execute('''
        SELECT crop_name, log_1_sentence, log_1_keyword_detected,
               log_2_sentence, log_2_keyword_detected,
               log_3_sentence, log_3_keyword_detected,
               log_4_sentence, log_4_keyword_detected,
               log_5_sentence, log_5_keyword_detected
        FROM test_results 
        WHERE session_id = ?
        ORDER BY id
    ''', (session_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['QA Name', 'Crop Name', 'Result', 'Language']
    for i in range(1, 6):
        header.extend([f'Log {i} Output', f'Log {i} Keyword Detected'])
    writer.writerow(header)
    
    # Write data
    for result in results:
        crop_name = result[0]
        correct_count = 0
        
        row = [qa_name, crop_name, language]
        
        for i in range(1, 11, 2):
            sentence = result[i] if result[i] else ""
            detected = result[i+1] if result[i+1] is not None else False
            row.extend([sentence, detected])
            if detected:
                correct_count += 1
        
        row[2] = f"{correct_count}/5"  # Update result
        writer.writerow(row)
    
    # Prepare file for download
    output.seek(0)
    csv_data = output.getvalue()
    output.close()
    
    # Create file-like object
    csv_file = io.BytesIO()
    csv_file.write(csv_data.encode('utf-8'))
    csv_file.seek(0)
    
    return send_file(
        csv_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'asr_test_results_{qa_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)