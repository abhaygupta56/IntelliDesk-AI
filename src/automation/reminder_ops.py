"""
Reminder Operations Module - FIXED
Flexible parameter handling for Groq compatibility
"""

import threading
import time
from datetime import datetime, timedelta
from src.utils.logger import Logger
from src.database.db_manager import DatabaseManager

logger = Logger.get_logger("Reminder")


class ReminderManager:
    """Reminder and timer operations"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.active_timers = {}
        self._init_reminders_table()
    
    def _init_reminders_table(self):
        """Create reminders table"""
        try:
            conn = self.db.get_connection()
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    remind_time TEXT NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to create reminders table: {e}")
    
    def create_reminder(self, title: str, remind_at: datetime, description: str = ""):
        """Create a reminder"""
        try:
            conn = self.db.get_connection()
            
            remind_time_str = remind_at.strftime("%Y-%m-%d %H:%M:%S")
            
            conn.execute(
                """INSERT INTO reminders (title, description, remind_time) 
                   VALUES (?, ?, ?)""",
                (title, description, remind_time_str)
            )
            conn.commit()
            
            # Schedule notification
            self._schedule_notification(title, remind_at)
            
            time_str = remind_at.strftime("%I:%M %p on %B %d")
            logger.info(f"✅ Reminder created: {title} at {time_str}")
            
            return {
                "status": "success",
                "message": f"Reminder set: {title} at {time_str}",
                "data": {"title": title, "time": time_str}
            }
        except Exception as e:
            logger.error(f"Failed to create reminder: {e}")
            return {"status": "error", "message": str(e)}
    
    def remind_in(self, title: str, minutes: int, description: str = ""):
        """Create reminder X minutes from now"""
        remind_at = datetime.now() + timedelta(minutes=minutes)
        return self.create_reminder(title, remind_at, description)
    
    def remind_at_time(self, title: str, hour: int, minute: int = 0, description: str = ""):
        """Create reminder at specific time today"""
        now = datetime.now()
        remind_at = now.replace(hour=hour, minute=minute, second=0)
        
        if remind_at <= now:
            remind_at += timedelta(days=1)
        
        return self.create_reminder(title, remind_at, description)
    
    def get_reminders(self, include_completed: bool = False):
        """Get all reminders"""
        try:
            conn = self.db.get_connection()
            
            if include_completed:
                cursor = conn.execute(
                    "SELECT * FROM reminders ORDER BY remind_time ASC"
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM reminders WHERE is_completed = 0 ORDER BY remind_time ASC"
                )
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"],
                    "remind_time": row["remind_time"],
                    "is_completed": bool(row["is_completed"])
                })
            
            if reminders:
                msg = f"You have {len(reminders)} reminder(s)"
            else:
                msg = "No active reminders"
            
            return {
                "status": "success",
                "message": msg,
                "data": {"reminders": reminders, "count": len(reminders)}
            }
        except Exception as e:
            logger.error(f"Failed to get reminders: {e}")
            return {"status": "error", "message": str(e)}
    
    def complete_reminder(self, reminder_id: int):
        """Mark reminder as completed"""
        try:
            conn = self.db.get_connection()
            conn.execute(
                "UPDATE reminders SET is_completed = 1 WHERE id = ?",
                (reminder_id,)
            )
            conn.commit()
            
            logger.info(f"Reminder {reminder_id} completed")
            return {"status": "success", "message": "Reminder completed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def delete_reminder(self, reminder_id: int):
        """Delete reminder"""
        try:
            conn = self.db.get_connection()
            conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            
            logger.info(f"Reminder {reminder_id} deleted")
            return {"status": "success", "message": "Reminder deleted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def start_timer(self, seconds: int, name: str = "Timer"):
        """Start a countdown timer"""
        try:
            timer_id = f"timer_{int(time.time())}"
            
            def timer_callback():
                self._show_notification(f"⏰ {name}", "Timer completed!")
                logger.info(f"⏰ Timer '{name}' completed!")
                if timer_id in self.active_timers:
                    del self.active_timers[timer_id]
            
            timer = threading.Timer(seconds, timer_callback)
            timer.start()
            
            self.active_timers[timer_id] = {
                "timer": timer,
                "name": name,
                "seconds": seconds,
                "started_at": datetime.now()
            }
            
            # Format time string
            if seconds >= 60:
                mins, secs = divmod(seconds, 60)
                time_str = f"{mins}m {secs}s" if secs else f"{mins} minutes"
            else:
                time_str = f"{seconds} seconds"
            
            logger.info(f"✅ Timer started: {name} for {time_str}")
            
            return {
                "status": "success",
                "message": f"Timer started for {time_str}",
                "data": {"timer_id": timer_id, "duration": time_str, "name": name}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def stop_timer(self, timer_id: str = None):
        """Stop a timer"""
        try:
            if timer_id and timer_id in self.active_timers:
                self.active_timers[timer_id]["timer"].cancel()
                del self.active_timers[timer_id]
                return {"status": "success", "message": "Timer stopped"}
            elif not timer_id and self.active_timers:
                count = len(self.active_timers)
                for tid, data in list(self.active_timers.items()):
                    data["timer"].cancel()
                    del self.active_timers[tid]
                return {"status": "success", "message": f"Stopped {count} timer(s)"}
            else:
                return {"status": "success", "message": "No active timers"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _schedule_notification(self, title: str, remind_at: datetime):
        """Schedule notification"""
        delay = (remind_at - datetime.now()).total_seconds()
        
        if delay > 0:
            timer = threading.Timer(delay, lambda: self._show_notification("⏰ Reminder", title))
            timer.start()
    
    def _show_notification(self, title: str, message: str):
        """Show desktop notification"""
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
        except:
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
            except:
                logger.info(f"🔔 NOTIFICATION: {title} - {message}")
                print(f"\n🔔 {title}: {message}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════
_reminder = ReminderManager()


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS - Flexible parameter handling for Groq
# ═══════════════════════════════════════════════════════════════════════════════

def remind_in(title=None, minutes=None, description="", message=None, event=None, time=None, **kwargs):
    """
    Set reminder X minutes from now
    Handles multiple parameter names from Groq
    """
    # Handle different parameter names
    reminder_title = title or message or event or "Reminder"
    reminder_mins = minutes or time or 5
    
    return _reminder.remind_in(str(reminder_title), int(reminder_mins), description)


def remind_at(title=None, hour=None, minute=0, description="", message=None, event=None, **kwargs):
    """
    Set reminder at specific time
    Handles multiple parameter names from Groq
    """
    reminder_title = title or message or event or "Reminder"
    
    if hour is None:
        return {"status": "error", "message": "Please specify the hour"}
    
    return _reminder.remind_at_time(str(reminder_title), int(hour), int(minute), description)


def get_reminders(**kwargs):
    """Get all active reminders"""
    return _reminder.get_reminders()


def complete_reminder(reminder_id=None, id=None, **kwargs):
    """Mark reminder as completed"""
    rid = reminder_id or id
    if rid is None:
        return {"status": "error", "message": "Please specify reminder ID"}
    return _reminder.complete_reminder(int(rid))


def delete_reminder(reminder_id=None, id=None, **kwargs):
    """Delete reminder"""
    rid = reminder_id or id
    if rid is None:
        return {"status": "error", "message": "Please specify reminder ID"}
    return _reminder.delete_reminder(int(rid))


def start_timer(seconds=None, time=None, duration=None, name="Timer", timer=None, event=None, action=None, **kwargs):
    """
    Start countdown timer
    Handles multiple parameter names from Groq:
    - seconds, time, duration, timer -> duration in seconds
    - name, event, action -> timer name
    """
    # Get duration from various parameter names
    timer_duration = seconds or time or duration or timer or 30
    
    # Get name from various parameter names
    timer_name = name if name != "Timer" else (event or action or "Timer")
    
    return _reminder.start_timer(int(timer_duration), str(timer_name))


def stop_timer(timer_id=None, **kwargs):
    """Stop active timer"""
    return _reminder.stop_timer(timer_id)


def set_timer(seconds=None, time=None, duration=None, name="Timer", timer=None, event=None, action=None, **kwargs):
    """
    Alias for start_timer - Groq often calls this name
    """
    return start_timer(seconds=seconds, time=time, duration=duration, name=name, timer=timer, event=event, action=action, **kwargs)