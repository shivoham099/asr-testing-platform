#!/usr/bin/env python3
"""
Supabase Database Service for ASR Testing Platform
Handles all database operations using Supabase
"""

import os
from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://cfjjlmkarwukmvhrqrtz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmampsbWthcnd1a212aHJxcnR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg0Njg2NjksImV4cCI6MjA3NDA0NDY2OX0.cFm3lnJh_nlIT0puxqbb6lBHMxDL9xY4cRudkeBfEQk"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_database():
    """Initialize database tables if they don't exist"""
    # This will be handled by SQL commands in Supabase dashboard
    pass

def create_qa_user(name, email):
    """Create or get QA user"""
    try:
        # Check if user already exists
        result = supabase.table('qa_users').select('*').eq('email', email).execute()
        
        if result.data:
            return result.data[0]['id']
        
        # Create new user
        result = supabase.table('qa_users').insert({
            'name': name,
            'email': email,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return result.data[0]['id']
    except Exception as e:
        print(f"Error creating QA user: {e}")
        return None

def create_test_session(qa_user_id, language):
    """Create a new test session"""
    try:
        result = supabase.table('test_sessions').insert({
            'qa_user_id': qa_user_id,
            'language': language,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return result.data[0]['id']
    except Exception as e:
        print(f"Error creating test session: {e}")
        return None

def get_test_session(session_id):
    """Get test session details"""
    try:
        result = supabase.table('test_sessions').select('*, qa_users(*)').eq('id', session_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting test session: {e}")
        return None

def create_test_result(session_id, crop_name):
    """Create a new test result record"""
    try:
        result = supabase.table('test_results').insert({
            'session_id': session_id,
            'crop_name': crop_name,
            'total_attempts': 5,
            'correct_attempts': 0,
            'result_ratio': '0/5',
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return result.data[0]['id']
    except Exception as e:
        print(f"Error creating test result: {e}")
        return None

def update_test_result(session_id, crop_name, attempt_number, transcript, keyword_detected):
    """Update test result with new attempt"""
    try:
        # Get existing result
        result = supabase.table('test_results').select('*').eq('session_id', session_id).eq('crop_name', crop_name).execute()
        
        if not result.data:
            # Create new result if doesn't exist
            create_test_result(session_id, crop_name)
            result = supabase.table('test_results').select('*').eq('session_id', session_id).eq('crop_name', crop_name).execute()
        
        existing_result = result.data[0]
        
        # Update the specific log
        log_sentence_key = f'log_{attempt_number}_sentence'
        log_detected_key = f'log_{attempt_number}_keyword_detected'
        
        update_data = {
            log_sentence_key: transcript,
            log_detected_key: keyword_detected
        }
        
        # Count correct attempts
        correct_count = 0
        for i in range(1, 6):
            detected = existing_result.get(f'log_{i}_keyword_detected', False)
            if detected:
                correct_count += 1
        
        # Update correct count if this attempt was successful
        if keyword_detected:
            correct_count += 1
        
        update_data['correct_attempts'] = correct_count
        update_data['result_ratio'] = f"{correct_count}/5"
        
        # Update the record
        supabase.table('test_results').update(update_data).eq('id', existing_result['id']).execute()
        
        return True
    except Exception as e:
        print(f"Error updating test result: {e}")
        return False

def get_test_results(session_id):
    """Get all test results for a session"""
    try:
        result = supabase.table('test_results').select('*').eq('session_id', session_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting test results: {e}")
        return []

def get_all_sessions():
    """Get all test sessions for admin dashboard"""
    try:
        result = supabase.table('test_sessions').select('*, qa_users(*)').order('created_at', desc=True).execute()
        return result.data
    except Exception as e:
        print(f"Error getting all sessions: {e}")
        return []

def get_all_users():
    """Get all QA users for admin dashboard"""
    try:
        result = supabase.table('qa_users').select('*').order('created_at', desc=True).execute()
        return result.data
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []



