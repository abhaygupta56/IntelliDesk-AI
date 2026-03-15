-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT DEFAULT 'default_user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat History
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    model_used TEXT,
    language TEXT
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    task_type TEXT NOT NULL,
    command TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    result TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP
);

-- Reminders
CREATE TABLE IF NOT EXISTS reminders (
    reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    title TEXT NOT NULL,
    description TEXT,
    reminder_time TIMESTAMP NOT NULL,
    is_completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API Usage Tracking
CREATE TABLE IF NOT EXISTS api_usage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_name TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    request_count INTEGER DEFAULT 1,
    date DATE DEFAULT CURRENT_DATE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_api_date ON api_usage(date);

-- Insert default user
INSERT OR IGNORE INTO users (user_id, username) VALUES (1, 'default_user');