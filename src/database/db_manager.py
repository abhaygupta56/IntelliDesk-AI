"""
Database Manager for IntelliDesk AI
Singleton pattern for performance
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from config import Config
from src.utils.logger import Logger

logger = Logger.get_logger("Database")


class DatabaseManager:
    """Handles all database operations - Singleton pattern"""
    
    _instance = None
    _initialized = False
    _connection = None
    
    def __new__(cls):
        """Ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize only once"""
        if not DatabaseManager._initialized:
            self.db_path = Config.DATABASE_PATH
            self.initialize_database()
            DatabaseManager._initialized = True
    
    def get_connection(self):
        """Get database connection (reuses existing connection)"""
        if DatabaseManager._connection is None:
            DatabaseManager._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            DatabaseManager._connection.row_factory = sqlite3.Row
        return DatabaseManager._connection
    
    def initialize_database(self):
        """Create tables if they don't exist (runs only once)"""
        try:
            schema_path = Path(__file__).parent / "schema.sql"
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            conn = self.get_connection()
            conn.executescript(schema)
            conn.commit()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    # ===== CHAT HISTORY =====
    
    def save_message(self, role, message, tokens=0, model="", language="en"):
        """Save chat message"""
        try:
            conn = self.get_connection()
            conn.execute("""
                INSERT INTO chat_history (role, message, tokens_used, model_used, language)
                VALUES (?, ?, ?, ?, ?)
            """, (role, message, tokens, model, language))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return False
    
    def get_recent_messages(self, limit=10):
        """Get recent chat history"""
        try:
            conn = self.get_connection()
            cursor = conn.execute("""
                SELECT role, message, timestamp, model_used
                FROM chat_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "role": row["role"],
                    "message": row["message"],
                    "timestamp": row["timestamp"],
                    "model": row["model_used"]
                })
            
            return list(reversed(messages))  # Oldest first
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    def clear_chat_history(self):
        """Clear all chat history"""
        try:
            conn = self.get_connection()
            conn.execute("DELETE FROM chat_history")
            conn.commit()
            logger.info("Chat history cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False
    
    # ===== TASKS =====
    
    def save_task(self, task_type, command, status="pending"):
        """Save task"""
        try:
            conn = self.get_connection()
            cursor = conn.execute("""
                INSERT INTO tasks (task_type, command, status)
                VALUES (?, ?, ?)
            """, (task_type, command, status))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save task: {e}")
            return None
    
    def update_task(self, task_id, status, result=None, error=None):
        """Update task status"""
        try:
            conn = self.get_connection()
            conn.execute("""
                UPDATE tasks
                SET status = ?, result = ?, error_message = ?, executed_at = ?
                WHERE task_id = ?
            """, (status, result, error, datetime.now(), task_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False
    
    def get_recent_tasks(self, limit=20):
        """Get recent tasks"""
        try:
            conn = self.get_connection()
            cursor = conn.execute("""
                SELECT * FROM tasks
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    # ===== API USAGE =====
    
    def log_api_usage(self, api_name, tokens=0):
        """Log API usage"""
        try:
            conn = self.get_connection()
            today = datetime.now().date()
            
            # Check if entry exists for today
            cursor = conn.execute("""
                SELECT usage_id, tokens_used, request_count
                FROM api_usage
                WHERE api_name = ? AND date = ?
            """, (api_name, today))
            
            row = cursor.fetchone()
            
            if row:
                # Update existing
                conn.execute("""
                    UPDATE api_usage
                    SET tokens_used = tokens_used + ?, request_count = request_count + 1
                    WHERE usage_id = ?
                """, (tokens, row["usage_id"]))
            else:
                # Insert new
                conn.execute("""
                    INSERT INTO api_usage (api_name, tokens_used, request_count, date)
                    VALUES (?, ?, 1, ?)
                """, (api_name, tokens, today))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")
            return False
    
    def get_api_usage_today(self, api_name):
        """Get today's API usage"""
        try:
            conn = self.get_connection()
            today = datetime.now().date()
            
            cursor = conn.execute("""
                SELECT tokens_used, request_count
                FROM api_usage
                WHERE api_name = ? AND date = ?
            """, (api_name, today))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "tokens": row["tokens_used"],
                    "requests": row["request_count"]
                }
            return {"tokens": 0, "requests": 0}
        except Exception as e:
            logger.error(f"Failed to get API usage: {e}")
            return {"tokens": 0, "requests": 0}
    
    def close(self):
        """Close database connection"""
        if DatabaseManager._connection:
            DatabaseManager._connection.close()
            DatabaseManager._connection = None
            DatabaseManager._initialized = False