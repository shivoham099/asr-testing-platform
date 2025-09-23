import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_qa_user(user_email: str, user_name: str) -> Dict[str, Any]:
    """Create a new QA user in Supabase"""
    try:
        result = supabase.table('qa_users').insert({
            'email': user_email,
            'name': user_name,
            'created_at': 'now()'
        }).execute()
        
        logger.info(f"Created QA user: {user_email}")
        return result.data[0] if result.data else {}
        
    except Exception as e:
        logger.error(f"Error creating QA user: {e}")
        raise

def create_test_session(user_id: int, language: str, total_crops: int) -> Dict[str, Any]:
    """Create a new test session in Supabase"""
    try:
        result = supabase.table('test_sessions').insert({
            'user_id': user_id,
            'language': language,
            'total_crops': total_crops,
            'status': 'active',
            'created_at': 'now()'
        }).execute()
        
        logger.info(f"Created test session for user {user_id}")
        return result.data[0] if result.data else {}
        
    except Exception as e:
        logger.error(f"Error creating test session: {e}")
        raise

def get_test_session(session_id: int) -> Optional[Dict[str, Any]]:
    """Get a test session by ID"""
    try:
        result = supabase.table('test_sessions').select('*').eq('id', session_id).execute()
        return result.data[0] if result.data else None
        
    except Exception as e:
        logger.error(f"Error getting test session: {e}")
        return None

def create_test_result(session_id: int, crop_name: str, transcript: str, 
                      keyword_detected: bool, attempt_number: int = 1) -> Dict[str, Any]:
    """Create a new test result in Supabase"""
    try:
        result = supabase.table('test_results').insert({
            'session_id': session_id,
            'crop_name': crop_name,
            'transcript': transcript,
            'keyword_detected': keyword_detected,
            'attempt_number': attempt_number,
            'created_at': 'now()'
        }).execute()
        
        logger.info(f"Created test result for session {session_id}")
        return result.data[0] if result.data else {}
        
    except Exception as e:
        logger.error(f"Error creating test result: {e}")
        raise

def update_test_result(result_id: int, transcript: str, keyword_detected: bool) -> Dict[str, Any]:
    """Update an existing test result"""
    try:
        result = supabase.table('test_results').update({
            'transcript': transcript,
            'keyword_detected': keyword_detected,
            'updated_at': 'now()'
        }).eq('id', result_id).execute()
        
        logger.info(f"Updated test result {result_id}")
        return result.data[0] if result.data else {}
        
    except Exception as e:
        logger.error(f"Error updating test result: {e}")
        raise

def get_test_results(session_id: int) -> List[Dict[str, Any]]:
    """Get all test results for a session"""
    try:
        result = supabase.table('test_results').select('*').eq('session_id', session_id).execute()
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting test results: {e}")
        return []

def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all test sessions"""
    try:
        result = supabase.table('test_sessions').select('*, qa_users(*)').order('created_at', desc=True).execute()
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting all sessions: {e}")
        return []

def get_all_users() -> List[Dict[str, Any]]:
    """Get all QA users"""
    try:
        result = supabase.table('qa_users').select('*').order('created_at', desc=True).execute()
        return result.data or []
        
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []
