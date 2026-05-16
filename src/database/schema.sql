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

-- ═══════════════════════════════════════════════════════════════════════════
-- LONG-TERM MEMORY: Extracted facts & preferences about the user
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_memory (
    memory_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_type TEXT    NOT NULL,   -- 'fact', 'habit', 'preference', 'person', 'recurring'
    key         TEXT    NOT NULL,   -- e.g. 'boss_name', 'preferred_browser', 'work_start'
    value       TEXT    NOT NULL,   -- e.g. 'Rahul', 'chrome', '9 AM'
    source      TEXT    DEFAULT '', -- the raw utterance that triggered this memory
    confidence  REAL    DEFAULT 1.0,
    seen_count  INTEGER DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(memory_type, key) ON CONFLICT REPLACE
);

-- ═══════════════════════════════════════════════════════════════════════════
-- USAGE PATTERNS: Which tools / apps the user uses and when
-- ═══════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS usage_patterns (
    pattern_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    action      TEXT    NOT NULL,       -- e.g. 'tool:open_app', 'app:chrome', 'intent:whatsapp'
    detail      TEXT    DEFAULT '',     -- extra context (e.g. which app, which contact)
    hour_of_day INTEGER DEFAULT -1,     -- 0-23, -1 = not tracked
    day_of_week INTEGER DEFAULT -1,     -- 0=Mon … 6=Sun, -1 = not tracked
    count       INTEGER DEFAULT 1,
    last_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(action, detail, hour_of_day) ON CONFLICT REPLACE
);

-- Memory indexes
CREATE INDEX IF NOT EXISTS idx_memory_type  ON user_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_seen  ON user_memory(last_seen);
CREATE INDEX IF NOT EXISTS idx_pattern_act  ON usage_patterns(action);
CREATE INDEX IF NOT EXISTS idx_pattern_hour ON usage_patterns(hour_of_day);