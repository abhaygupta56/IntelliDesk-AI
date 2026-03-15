"""
WhatsApp Automation Module - Fixed for Groq
Smart handling with **kwargs to avoid parameter conflicts
"""

import pywhatkit as kit
import pyautogui
import time
import re
import os
from datetime import datetime
from src.database.db_manager import DatabaseManager
from src.utils.logger import Logger

logger = Logger.get_logger("WhatsApp")


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class ContactManager:
    """Manage WhatsApp contacts in database"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_contacts_table()
    
    def _init_contacts_table(self):
        """Create contacts table"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS whatsapp_contacts (
                    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_messaged TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create contacts table: {e}")
    
    def save_contact(self, name, phone):
        """Save or update contact"""
        try:
            conn = self.db.get_connection()
            name_lower = name.lower().strip()
            
            cursor = conn.execute(
                "SELECT contact_id FROM whatsapp_contacts WHERE name = ?",
                (name_lower,)
            )
            existing = cursor.fetchone()
            
            if existing:
                conn.execute(
                    "UPDATE whatsapp_contacts SET phone = ? WHERE name = ?",
                    (phone, name_lower)
                )
                logger.info(f"Updated contact: {name}")
            else:
                conn.execute(
                    "INSERT INTO whatsapp_contacts (name, phone) VALUES (?, ?)",
                    (name_lower, phone)
                )
                logger.info(f"Saved new contact: {name}")
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save contact: {e}")
            return False
    
    def get_contact(self, name):
        """Get phone number by name"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT phone FROM whatsapp_contacts WHERE name = ?",
                (name.lower().strip(),)
            )
            row = cursor.fetchone()
            return row["phone"] if row else None
        except Exception as e:
            logger.error(f"Failed to get contact: {e}")
            return None
    
    def search_contacts(self, query):
        """Search contacts by partial name"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT name, phone FROM whatsapp_contacts WHERE name LIKE ?",
                (f"%{query.lower()}%",)
            )
            return [{"name": row["name"], "phone": row["phone"]} for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_all_contacts(self):
        """Get all saved contacts"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT name, phone FROM whatsapp_contacts ORDER BY name"
            )
            return [{"name": row["name"], "phone": row["phone"]} for row in cursor.fetchall()]
        except Exception as e:
            return []
    
    def delete_contact(self, name):
        """Delete a contact"""
        try:
            conn = self.db.get_connection()
            conn.execute("DELETE FROM whatsapp_contacts WHERE name = ?", (name.lower(),))
            conn.commit()
            return True
        except:
            return False
    
    def update_last_messaged(self, name):
        """Update last messaged timestamp"""
        try:
            conn = self.db.get_connection()
            conn.execute(
                "UPDATE whatsapp_contacts SET last_messaged = ? WHERE name = ?",
                (datetime.now(), name.lower())
            )
            conn.commit()
        except:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# WHATSAPP CORE
# ═══════════════════════════════════════════════════════════════════════════════

class WhatsAppAutomation:
    
    def __init__(self):
        self.wait_time = 15
        self.retry_attempts = 2
        self.contacts = ContactManager()
        self.db = DatabaseManager()
        self._init_message_history()
    
    def _init_message_history(self):
        """Create message history table"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS whatsapp_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    message TEXT NOT NULL,
                    msg_type TEXT DEFAULT 'text',
                    status TEXT DEFAULT 'sent',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create history table: {e}")
    
    def is_phone_number(self, text):
        """Check if text is a phone number"""
        if not text:
            return False
        cleaned = re.sub(r'[\s\-\(\)\+]', '', str(text))
        return len(cleaned) >= 10 and cleaned.isdigit()
    
    def format_phone(self, phone):
        """Format phone to +91XXXXXXXXXX"""
        phone = re.sub(r'[\s\-\(\)]', '', str(phone))
        
        if not phone.startswith('+'):
            if not phone.startswith('91'):
                phone = '91' + phone
            phone = '+' + phone
        
        if len(phone) < 13:
            raise ValueError(f"Invalid phone: {phone}")
        
        return phone
    
    def resolve_recipient(self, recipient):
        """Convert name to phone or validate phone"""
        if self.is_phone_number(recipient):
            return self.format_phone(recipient)
        
        phone = self.contacts.get_contact(recipient)
        if phone:
            return phone
        
        matches = self.contacts.search_contacts(recipient)
        if len(matches) == 1:
            return matches[0]["phone"]
        
        return None
    
    def send_message_core(self, phone, message):
        """Core send with retry"""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Sending WhatsApp (attempt {attempt + 1})...")
                
                kit.sendwhatmsg_instantly(
                    phone_no=phone,
                    message=message,
                    wait_time=self.wait_time,
                    tab_close=True,
                    close_time=3
                )
                
                time.sleep(2)
                pyautogui.press('enter')
                
                logger.info(f"✅ WhatsApp sent to {phone}")
                return True
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2)
        
        return False
    
    def send_image_core(self, phone, image_path, caption=""):
        """Send image"""
        try:
            kit.sendwhats_image(
                receiver=phone,
                img_path=image_path,
                caption=caption,
                wait_time=self.wait_time,
                tab_close=True,
                close_time=3
            )
            
            time.sleep(2)
            pyautogui.press('enter')
            logger.info(f"✅ Image sent to {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Image send failed: {e}")
            return False
    
    def save_to_history(self, recipient, phone, message, msg_type="text"):
        """Save to history"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                INSERT INTO whatsapp_history (recipient, phone, message, msg_type)
                VALUES (?, ?, ?, ?)
            """, (recipient, phone, message, msg_type))
            conn.commit()
        except:
            pass
    
    def get_history(self, limit=20):
        """Get message history"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute("""
                SELECT recipient, phone, message, msg_type, timestamp
                FROM whatsapp_history ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_wa = WhatsAppAutomation()


# ═══════════════════════════════════════════════════════════════════════════════
# GROQ-FRIENDLY FUNCTIONS - All use **kwargs
# ═══════════════════════════════════════════════════════════════════════════════

def send_whatsapp(**kwargs):
    """
    Smart WhatsApp sender
    Handles all parameter name variations from Groq
    """
    
    # Extract with flexible parameter names
    recipient = (
        kwargs.get('recipient') or 
        kwargs.get('to') or 
        kwargs.get('contact') or 
        kwargs.get('name')
    )
    
    message = (
        kwargs.get('message') or 
        kwargs.get('msg') or 
        kwargs.get('text')
    )
    
    phone = (
        kwargs.get('phone') or 
        kwargs.get('number')
    )
    
    # Validation
    if not recipient:
        return {
            "status": "needs_info",
            "message": "Who do you want to send WhatsApp to?",
            "data": {"missing": "recipient"}
        }
    
    if not message:
        return {
            "status": "needs_info",
            "message": f"What message for {recipient}?",
            "data": {"missing": "message", "recipient": recipient}
        }
    
    # Send to phone number directly
    if _wa.is_phone_number(recipient):
        try:
            formatted = _wa.format_phone(recipient)
            if _wa.send_message_core(formatted, message):
                _wa.save_to_history(recipient, formatted, message)
                return {
                    "status": "success",
                    "message": f"WhatsApp sent to {formatted}",
                    "data": {"phone": formatted}
                }
            return {"status": "error", "message": "Failed to send"}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
    
    # Lookup contact
    resolved = _wa.resolve_recipient(recipient)
    
    if resolved:
        if _wa.send_message_core(resolved, message):
            _wa.contacts.update_last_messaged(recipient)
            _wa.save_to_history(recipient, resolved, message)
            return {
                "status": "success",
                "message": f"WhatsApp sent to {recipient}",
                "data": {"recipient": recipient, "phone": resolved}
            }
        return {"status": "error", "message": "Failed to send"}
    
    # Save and send if phone provided
    if phone:
        try:
            formatted = _wa.format_phone(phone)
            _wa.contacts.save_contact(recipient, formatted)
            
            if _wa.send_message_core(formatted, message):
                _wa.save_to_history(recipient, formatted, message)
                return {
                    "status": "success",
                    "message": f"Contact saved and WhatsApp sent to {recipient}",
                    "data": {"contact_saved": True}
                }
            return {"status": "error", "message": "Saved but send failed"}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
    
    # No contact found
    return {
        "status": "needs_info",
        "message": f"I don't have {recipient}'s number. Please provide it.",
        "data": {"missing": "phone", "recipient": recipient, "message": message}
    }


def save_whatsapp_contact(**kwargs):
    """Save WhatsApp contact"""
    
    cname = kwargs.get('name') or kwargs.get('contact')
    cphone = kwargs.get('phone') or kwargs.get('number')
    
    if not cname:
        return {"status": "needs_info", "message": "What name?"}
    
    if not cphone:
        return {"status": "needs_info", "message": f"What is {cname}'s phone?"}
    
    try:
        formatted = _wa.format_phone(cphone)
        if _wa.contacts.save_contact(cname, formatted):
            return {
                "status": "success",
                "message": f"Contact saved: {cname} → {formatted}",
                "data": {"name": cname, "phone": formatted}
            }
        return {"status": "error", "message": "Failed to save"}
    except ValueError as e:
        return {"status": "error", "message": str(e)}


def list_whatsapp_contacts(**kwargs):
    """List all WhatsApp contacts"""
    
    contacts = _wa.contacts.get_all_contacts()
    
    if contacts:
        text = "\n".join([f"• {c['name']}: {c['phone']}" for c in contacts[:10]])
        return {
            "status": "success",
            "message": f"You have {len(contacts)} contacts:\n{text}",
            "data": {"contacts": contacts, "count": len(contacts)}
        }
    return {
        "status": "success",
        "message": "No contacts saved yet"
    }


def send_whatsapp_file(**kwargs):
    """Send file on WhatsApp"""
    
    recipient = (
        kwargs.get('recipient') or 
        kwargs.get('to') or 
        kwargs.get('contact') or 
        kwargs.get('name')
    )
    
    file_path = kwargs.get('file_path') or kwargs.get('file')
    caption = kwargs.get('caption') or kwargs.get('message') or ""
    
    if not recipient:
        return {"status": "needs_info", "message": "Send file to whom?"}
    
    phone = _wa.resolve_recipient(recipient)
    if not phone:
        return {"status": "needs_info", "message": f"I don't have {recipient}'s number"}
    
    # Open file picker
    if not file_path:
        try:
            from tkinter import Tk, filedialog
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            file_path = filedialog.askopenfilename(
                title=f"Select file for {recipient}",
                filetypes=[
                    ("Images", "*.png *.jpg *.jpeg"),
                    ("Documents", "*.pdf *.docx *.txt"),
                    ("All", "*.*")
                ]
            )
            root.destroy()
            
            if not file_path:
                return {"status": "error", "message": "No file selected"}
        except Exception as e:
            return {"status": "error", "message": f"Picker error: {e}"}
    
    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found"}
    
    if _wa.send_image_core(phone, file_path, caption):
        _wa.save_to_history(recipient, phone, f"[FILE] {os.path.basename(file_path)}", "file")
        return {"status": "success", "message": f"File sent to {recipient}"}
    
    return {"status": "error", "message": "Failed to send file"}


def schedule_whatsapp(**kwargs):
    """Schedule WhatsApp message"""
    
    recipient = kwargs.get('recipient') or kwargs.get('to')
    message = kwargs.get('message') or kwargs.get('msg')
    hour = kwargs.get('hour')
    minute = kwargs.get('minute') or 0
    
    if not recipient:
        return {"status": "needs_info", "message": "Send to whom?"}
    if not message:
        return {"status": "needs_info", "message": "What message?"}
    if hour is None:
        return {"status": "needs_info", "message": "What time?"}
    
    phone = _wa.resolve_recipient(recipient)
    if not phone:
        return {"status": "needs_info", "message": f"No number for {recipient}"}
    
    try:
        kit.sendwhatmsg(phone, message, int(hour), int(minute), wait_time=15, tab_close=True)
        return {"status": "success", "message": f"Scheduled for {hour:02d}:{minute:02d}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed: {e}"}


def delete_whatsapp_contact(**kwargs):
    """Delete contact"""
    
    cname = kwargs.get('name') or kwargs.get('contact')
    
    if not cname:
        return {"status": "needs_info", "message": "Delete which contact?"}
    
    if _wa.contacts.delete_contact(cname):
        return {"status": "success", "message": f"{cname} deleted"}
    return {"status": "error", "message": f"{cname} not found"}


def whatsapp_history(**kwargs):
    """Get message history"""
    
    limit = kwargs.get('limit') or 10
    history = _wa.get_history(limit)
    
    if history:
        text = "\n".join([f"• {h['recipient']}: {h['message'][:30]}..." for h in history[:5]])
        return {"status": "success", "message": f"Recent:\n{text}"}
    
    return {"status": "success", "message": "No history"}


# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

send = send_whatsapp
save_contact = save_whatsapp_contact
list_contacts = list_whatsapp_contacts
send_file = send_whatsapp_file
schedule = schedule_whatsapp