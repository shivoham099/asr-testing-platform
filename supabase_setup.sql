-- Supabase Database Schema for ASR Testing Platform

-- QA Users table
CREATE TABLE IF NOT EXISTS qa_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test Sessions table
CREATE TABLE IF NOT EXISTS test_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES qa_users(id) ON DELETE CASCADE,
    language VARCHAR(50) NOT NULL,
    total_crops INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Test Results table
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES test_sessions(id) ON DELETE CASCADE,
    crop_name VARCHAR(255) NOT NULL,
    transcript TEXT,
    keyword_detected BOOLEAN DEFAULT FALSE,
    attempt_number INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_test_sessions_status ON test_sessions(status);
CREATE INDEX IF NOT EXISTS idx_test_results_session_id ON test_results(session_id);
CREATE INDEX IF NOT EXISTS idx_test_results_keyword_detected ON test_results(keyword_detected);

-- Enable Row Level Security (RLS)
ALTER TABLE qa_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_results ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations on qa_users" ON qa_users FOR ALL USING (true);
CREATE POLICY "Allow all operations on test_sessions" ON test_sessions FOR ALL USING (true);
CREATE POLICY "Allow all operations on test_results" ON test_results FOR ALL USING (true);
