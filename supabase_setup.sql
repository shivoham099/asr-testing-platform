-- Supabase Database Setup for ASR Testing Platform
-- Run these commands in Supabase SQL Editor

-- Create qa_users table
CREATE TABLE IF NOT EXISTS qa_users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test_sessions table
CREATE TABLE IF NOT EXISTS test_sessions (
    id SERIAL PRIMARY KEY,
    qa_user_id INTEGER REFERENCES qa_users(id) ON DELETE CASCADE,
    language TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test_results table
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES test_sessions(id) ON DELETE CASCADE,
    crop_name TEXT NOT NULL,
    total_attempts INTEGER DEFAULT 5,
    correct_attempts INTEGER DEFAULT 0,
    result_ratio TEXT DEFAULT '0/5',
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE qa_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_results ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (since we're using anon key)
CREATE POLICY "Allow all operations on qa_users" ON qa_users FOR ALL USING (true);
CREATE POLICY "Allow all operations on test_sessions" ON test_sessions FOR ALL USING (true);
CREATE POLICY "Allow all operations on test_results" ON test_results FOR ALL USING (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_test_sessions_qa_user_id ON test_sessions(qa_user_id);
CREATE INDEX IF NOT EXISTS idx_test_results_session_id ON test_results(session_id);
CREATE INDEX IF NOT EXISTS idx_test_results_crop_name ON test_results(crop_name);
