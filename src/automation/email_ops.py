"""
Email Automation Module - Fixed for Groq
Smart handling with **kwargs to avoid parameter conflicts
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import re
from datetime import datetime
from src.database.db_manager import DatabaseManager
from config import Config
from src.utils.logger import Logger

logger = Logger.get_logger("Email")


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL CONTACT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class EmailContactManager:
    """Manage email contacts in database"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_contacts_table()
    
    def _init_contacts_table(self):
        """Create email contacts table"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS email_contacts (
                    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    category TEXT DEFAULT 'personal',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_emailed TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create contacts table: {e}")
    
    def save_contact(self, name, email, category='personal'):
        """Save email contact"""
        try:
            conn = self.db.get_connection()
            name_lower = name.lower().strip()
            
            cursor = conn.execute(
                "SELECT contact_id FROM email_contacts WHERE name = ?",
                (name_lower,)
            )
            existing = cursor.fetchone()
            
            if existing:
                conn.execute(
                    "UPDATE email_contacts SET email = ?, category = ? WHERE name = ?",
                    (email, category, name_lower)
                )
                logger.info(f"Updated email contact: {name}")
            else:
                conn.execute(
                    "INSERT INTO email_contacts (name, email, category) VALUES (?, ?, ?)",
                    (name_lower, email, category)
                )
                logger.info(f"Saved email contact: {name} -> {email}")
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save contact: {e}")
            return False
    
    def get_contact(self, name):
        """Get email by name"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT email FROM email_contacts WHERE name = ?",
                (name.lower().strip(),)
            )
            row = cursor.fetchone()
            return row["email"] if row else None
        except Exception as e:
            logger.error(f"Failed to get contact: {e}")
            return None
    
    def search_contacts(self, query):
        """Search email contacts"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT name, email, category FROM email_contacts WHERE name LIKE ? OR email LIKE ?",
                (f"%{query.lower()}%", f"%{query.lower()}%")
            )
            return [{"name": row["name"], "email": row["email"], "category": row["category"]} 
                    for row in cursor.fetchall()]
        except:
            return []
    
    def get_all_contacts(self):
        """Get all email contacts"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT name, email, category FROM email_contacts ORDER BY name"
            )
            return [{"name": row["name"], "email": row["email"], "category": row["category"]} 
                    for row in cursor.fetchall()]
        except:
            return []
    
    def delete_contact(self, name):
        """Delete email contact"""
        try:
            conn = self.db.get_connection()
            conn.execute("DELETE FROM email_contacts WHERE name = ?", (name.lower(),))
            conn.commit()
            return True
        except:
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL CORE
# ═══════════════════════════════════════════════════════════════════════════════

class EmailAutomation:
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.sender = getattr(Config, 'EMAIL_ADDRESS', None)
        self.password = getattr(Config, 'EMAIL_PASSWORD', None)
        self.contacts = EmailContactManager()
        self.db = DatabaseManager()
        self._init_tables()
    
    def _init_tables(self):
        """Initialize email tables"""
        try:
            conn = self.db.get_connection()
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS email_history (
                    email_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient TEXT NOT NULL,
                    recipient_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT,
                    has_attachment BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'sent',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create email tables: {e}")
    
    def is_configured(self):
        """Check if email is configured"""
        return bool(self.sender and self.password)
    
    def is_email(self, text):
        """Check if text is email address"""
        if not text:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, str(text)) is not None
    
    def resolve_recipient(self, recipient):
        """Convert name to email or validate email"""
        if self.is_email(recipient):
            return recipient
        
        email = self.contacts.get_contact(recipient)
        if email:
            return email
        
        matches = self.contacts.search_contacts(recipient)
        if len(matches) == 1:
            return matches[0]["email"]
        
        return None
    
    def send_smtp(self, to_email, subject, body, attachment_path=None):
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Email authentication failed")
            return False
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
    
    def save_to_history(self, recipient, email, subject, body, has_attachment=False):
        """Save email to history"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                INSERT INTO email_history (recipient, recipient_email, subject, body, has_attachment)
                VALUES (?, ?, ?, ?, ?)
            """, (recipient, email, subject, body, has_attachment))
            conn.commit()
        except:
            pass
    
    def get_history(self, limit=20):
        """Get email history"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute("""
                SELECT recipient, recipient_email, subject, body, timestamp
                FROM email_history ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
    
    def save_template(self, name, subject, body):
        """Save email template"""
        try:
            conn = self.db.get_connection()
            
            cursor = conn.execute(
                "SELECT template_id FROM email_templates WHERE name = ?",
                (name.lower(),)
            )
            existing = cursor.fetchone()
            
            if existing:
                conn.execute(
                    "UPDATE email_templates SET subject = ?, body = ? WHERE name = ?",
                    (subject, body, name.lower())
                )
            else:
                conn.execute(
                    "INSERT INTO email_templates (name, subject, body) VALUES (?, ?, ?)",
                    (name.lower(), subject, body)
                )
            
            conn.commit()
            return True
        except:
            return False
    
    def get_template(self, name):
        """Get email template"""
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(
                "SELECT subject, body FROM email_templates WHERE name = ?",
                (name.lower(),)
            )
            row = cursor.fetchone()
            return {"subject": row["subject"], "body": row["body"]} if row else None
        except:
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_email = EmailAutomation()


# ═══════════════════════════════════════════════════════════════════════════════
# GROQ-FRIENDLY FUNCTIONS - All use **kwargs
# ═══════════════════════════════════════════════════════════════════════════════

def send_email(**kwargs):
    """
    Smart email sender
    Handles all parameter name variations from Groq
    """
    
    # Check if configured
    if not _email.is_configured():
        return {
            "status": "error",
            "message": "Email not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env file.",
            "data": {"hint": "Use Gmail App Password for security"}
        }
    
    # Extract with flexible parameter names
    recipient = (
        kwargs.get('recipient') or 
        kwargs.get('to') or 
        kwargs.get('contact') or 
        kwargs.get('name')
    )
    
    subject = (
        kwargs.get('subject') or 
        kwargs.get('title') or 
        kwargs.get('sub')
    )
    
    body = (
        kwargs.get('body') or 
        kwargs.get('message') or 
        kwargs.get('msg') or 
        kwargs.get('content') or
        kwargs.get('text')
    )
    
    email_addr = (
        kwargs.get('email') or 
        kwargs.get('email_address')
    )
    
    attachment = (
        kwargs.get('attachment') or 
        kwargs.get('attachment_path') or 
        kwargs.get('file')
    )
    
    # Validation
    if not recipient:
        return {
            "status": "needs_info",
            "message": "Who do you want to send the email to?",
            "data": {"missing": "recipient"}
        }
    
    if not subject:
        return {
            "status": "needs_info",
            "message": f"What's the subject of the email to {recipient}?",
            "data": {"missing": "subject", "recipient": recipient}
        }
    
    if not body:
        return {
            "status": "needs_info",
            "message": f"What should the email say?",
            "data": {"missing": "body", "recipient": recipient, "subject": subject}
        }
    
    # Send to email address directly
    if _email.is_email(recipient):
        if _email.send_smtp(recipient, subject, body, attachment):
            _email.save_to_history(recipient, recipient, subject, body, bool(attachment))
            return {
                "status": "success",
                "message": f"Email sent to {recipient}",
                "data": {"email": recipient, "subject": subject}
            }
        return {"status": "error", "message": "Failed to send email. Check credentials."}
    
    # Lookup contact
    resolved = _email.resolve_recipient(recipient)
    
    if resolved:
        if _email.send_smtp(resolved, subject, body, attachment):
            _email.save_to_history(recipient, resolved, subject, body, bool(attachment))
            return {
                "status": "success",
                "message": f"Email sent to {recipient} ({resolved})",
                "data": {"recipient": recipient, "email": resolved}
            }
        return {"status": "error", "message": "Failed to send email"}
    
    # Save and send if email address provided
    if email_addr:
        if not _email.is_email(email_addr):
            return {"status": "error", "message": f"Invalid email address: {email_addr}"}
        
        _email.contacts.save_contact(recipient, email_addr)
        
        if _email.send_smtp(email_addr, subject, body, attachment):
            _email.save_to_history(recipient, email_addr, subject, body, bool(attachment))
            return {
                "status": "success",
                "message": f"Contact saved and email sent to {recipient}",
                "data": {"contact_saved": True}
            }
        return {"status": "error", "message": "Saved contact but send failed"}
    
    # No contact found
    return {
        "status": "needs_info",
        "message": f"I don't have {recipient}'s email address. Please provide it.",
        "data": {"missing": "email", "recipient": recipient}
    }


def save_email_contact(**kwargs):
    """Save email contact"""
    
    cname = kwargs.get('name') or kwargs.get('contact')
    cemail = kwargs.get('email') or kwargs.get('email_address') or kwargs.get('address')
    category = kwargs.get('category') or 'personal'
    
    if not cname:
        return {"status": "needs_info", "message": "What name should I save?"}
    
    if not cemail:
        return {"status": "needs_info", "message": f"What is {cname}'s email?"}
    
    if not _email.is_email(cemail):
        return {"status": "error", "message": f"Invalid email: {cemail}"}
    
    if _email.contacts.save_contact(cname, cemail, category):
        return {
            "status": "success",
            "message": f"Contact saved: {cname} → {cemail}",
            "data": {"name": cname, "email": cemail}
        }
    return {"status": "error", "message": "Failed to save"}


def list_email_contacts(**kwargs):
    """List all email contacts"""
    
    contacts = _email.contacts.get_all_contacts()
    
    if contacts:
        text = "\n".join([f"• {c['name']}: {c['email']}" for c in contacts[:10]])
        return {
            "status": "success",
            "message": f"You have {len(contacts)} email contacts:\n{text}",
            "data": {"contacts": contacts, "count": len(contacts)}
        }
    return {"status": "success", "message": "No email contacts saved yet."}


def email_history(**kwargs):
    """Get email history"""
    
    limit = kwargs.get('limit') or 10
    history = _email.get_history(limit)
    
    if history:
        text = "\n".join([f"• {h['recipient']}: {h['subject'][:30]}..." for h in history[:5]])
        return {"status": "success", "message": f"Recent emails:\n{text}"}
    return {"status": "success", "message": "No email history yet"}


def delete_email_contact(**kwargs):
    """Delete email contact"""
    
    cname = kwargs.get('name') or kwargs.get('contact')
    
    if not cname:
        return {"status": "needs_info", "message": "Which contact to delete?"}
    
    if _email.contacts.delete_contact(cname):
        return {"status": "success", "message": f"{cname} deleted"}
    return {"status": "error", "message": f"{cname} not found"}


def save_email_template(**kwargs):
    """Save email template"""
    
    tname = kwargs.get('name') or kwargs.get('template_name')
    subject = kwargs.get('subject')
    body = kwargs.get('body') or kwargs.get('content')
    
    if not tname:
        return {"status": "needs_info", "message": "What's the template name?"}
    if not subject:
        return {"status": "needs_info", "message": "What's the subject?"}
    if not body:
        return {"status": "needs_info", "message": "What's the body?"}
    
    if _email.save_template(tname, subject, body):
        return {"status": "success", "message": f"Template '{tname}' saved"}
    return {"status": "error", "message": "Failed to save template"}


def use_email_template(**kwargs):
    """Use email template"""
    
    tname = kwargs.get('name') or kwargs.get('template_name') or kwargs.get('template')
    recipient = kwargs.get('recipient') or kwargs.get('to')
    
    if not tname:
        return {"status": "needs_info", "message": "Which template to use?"}
    
    template = _email.get_template(tname)
    
    if not template:
        return {"status": "error", "message": f"Template '{tname}' not found"}
    
    if recipient:
        # Send using template
        return send_email(
            recipient=recipient,
            subject=template['subject'],
            body=template['body']
        )
    
    return {
        "status": "success",
        "message": f"Template '{tname}':\nSubject: {template['subject']}\nBody: {template['body'][:100]}...",
        "data": template
    }


def check_email_config(**kwargs):
    """Check if email is configured"""
    
    if _email.is_configured():
        return {
            "status": "success",
            "message": f"Email configured: {_email.sender}",
            "data": {"configured": True, "email": _email.sender}
        }
    return {
        "status": "error",
        "message": "Email not configured. Add EMAIL_ADDRESS and EMAIL_PASSWORD to .env file",
        "data": {"configured": False}
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

send = send_email
save_contact = save_email_contact
list_contacts = list_email_contacts
history = email_history