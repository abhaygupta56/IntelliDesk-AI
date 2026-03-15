"""
Utility Operations Module
Features:
- Date/Time
- Calculator
- Password generator
- Text to speech
- Translate
- Notes
- Timer
- Random number
"""

import os
import random
import string
import math
from datetime import datetime, timedelta
from pathlib import Path
from src.utils.logger import Logger
from src.database.db_manager import DatabaseManager

logger = Logger.get_logger("Utility")


class UtilityManager:
    """Utility operations"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_notes_table()
    
    def _init_notes_table(self):
        """Create notes table"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create notes table: {e}")
    
    def get_time(self):
        """Get current time"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        
        logger.info(f"Current time: {time_str}")
        
        return {
            "status": "success",
            "message": f"Current time is {time_str}",
            "data": {
                "time": time_str,
                "time_24": now.strftime("%H:%M:%S")
            }
        }
    
    def get_date(self):
        """Get current date"""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        
        logger.info(f"Current date: {date_str}")
        
        return {
            "status": "success",
            "message": f"Today is {date_str}",
            "data": {
                "date": date_str,
                "date_short": now.strftime("%d/%m/%Y"),
                "day": now.strftime("%A")
            }
        }
    
    def calculate(self, expression: str):
        """Calculate math expression"""
        try:
            # Clean expression
            expression = expression.replace('x', '*').replace('×', '*')
            expression = expression.replace('÷', '/').replace('^', '**')
            
            # Safe evaluation
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return {"status": "error", "message": "Invalid characters in expression"}
            
            result = eval(expression)
            
            # Format result
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
            
            logger.info(f"Calculate: {expression} = {result}")
            
            return {
                "status": "success",
                "message": f"{expression} = {result}",
                "data": {"expression": expression, "result": result}
            }
        except ZeroDivisionError:
            return {"status": "error", "message": "Cannot divide by zero"}
        except Exception as e:
            return {"status": "error", "message": f"Invalid expression: {e}"}
    
    def generate_password(self, length: int = 12, include_special: bool = True):
        """Generate random password"""
        try:
            if length < 4:
                length = 4
            if length > 50:
                length = 50
            
            chars = string.ascii_letters + string.digits
            if include_special:
                chars += "!@#$%&*"
            
            # Ensure at least one of each type
            password = [
                random.choice(string.ascii_lowercase),
                random.choice(string.ascii_uppercase),
                random.choice(string.digits),
            ]
            
            if include_special:
                password.append(random.choice("!@#$%&*"))
            
            # Fill remaining
            remaining = length - len(password)
            password.extend(random.choices(chars, k=remaining))
            
            # Shuffle
            random.shuffle(password)
            password = ''.join(password)
            
            logger.info(f"Generated password of length {length}")
            
            return {
                "status": "success",
                "message": f"Generated password: {password}",
                "data": {"password": password, "length": length}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def text_to_speech(self, text: str):
        """Convert text to speech"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            
            logger.info(f"TTS: {text[:50]}...")
            
            return {
                "status": "success",
                "message": "Text spoken successfully"
            }
        except ImportError:
            # Fallback to system TTS
            try:
                import subprocess
                subprocess.run(
                    ['powershell', '-Command', f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'],
                    capture_output=True
                )
                return {"status": "success", "message": "Text spoken"}
            except:
                return {"status": "error", "message": "TTS not available. Install pyttsx3"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_note(self, content: str, title: str = None):
        """Create a quick note"""
        try:
            if not title:
                title = f"Note {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            conn = self.db.get_connection()
            conn.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                (title, content)
            )
            conn.commit()
            
            logger.info(f"✅ Note created: {title}")
            
            return {
                "status": "success",
                "message": f"Note saved: {title}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_notes(self, limit: int = 10):
        """Get recent notes"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            
            notes = []
            for row in cursor.fetchall():
                notes.append({
                    "id": row["id"],
                    "title": row["title"],
                    "content": row["content"][:100],
                    "created_at": row["created_at"]
                })
            
            return {
                "status": "success",
                "notes": notes,
                "count": len(notes)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def delete_note(self, note_id: int):
        """Delete a note"""
        try:
            conn = self.db.get_connection()
            conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            
            logger.info(f"Note {note_id} deleted")
            
            return {"status": "success", "message": "Note deleted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def random_number(self, min_val: int = 1, max_val: int = 100):
        """Generate random number"""
        try:
            num = random.randint(min_val, max_val)
            
            return {
                "status": "success",
                "message": f"Random number: {num}",
                "data": {"number": num, "min": min_val, "max": max_val}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def flip_coin(self):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        
        return {
            "status": "success",
            "message": f"Coin flip: {result}",
            "data": {"result": result}
        }
    
    def roll_dice(self, sides: int = 6):
        """Roll a dice"""
        result = random.randint(1, sides)
        
        return {
            "status": "success",
            "message": f"Dice roll: {result}",
            "data": {"result": result, "sides": sides}
        }


# Global instance
_utility = UtilityManager()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_time():
    return _utility.get_time()

def get_date():
    return _utility.get_date()

def calculate(expression):
    return _utility.calculate(expression)

def generate_password(length=12, include_special=True):
    return _utility.generate_password(length, include_special)

def speak(text):
    return _utility.text_to_speech(text)

def create_note(content, title=None):
    return _utility.create_note(content, title)

def get_notes(limit=10):
    return _utility.get_notes(limit)

def delete_note(note_id):
    return _utility.delete_note(note_id)

def random_number(min_val=1, max_val=100):
    return _utility.random_number(min_val, max_val)

def flip_coin():
    return _utility.flip_coin()

def roll_dice(sides=6):
    return _utility.roll_dice(sides)