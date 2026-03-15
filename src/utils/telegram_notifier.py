"""
Telegram Notifier - Send alerts with photos
"""

import requests
from datetime import datetime
from src.utils.logger import Logger
from config import Config

logger = Logger.get_logger("Telegram")


class TelegramNotifier:
    """Send alerts to Telegram"""
    
    def __init__(self):
        self.bot_token = getattr(Config, 'TELEGRAM_BOT_TOKEN', None)
        self.chat_id = getattr(Config, 'TELEGRAM_CHAT_ID', None)
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def is_configured(self):
        """Check if Telegram is set up"""
        return bool(self.bot_token and self.chat_id)
    
    def send_alert(self, message, photo_path=None):
        """Send text alert with optional photo"""
        try:
            if not self.is_configured():
                logger.error("Telegram not configured")
                return False
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"🚨 SENTRY ALERT\n\n{message}\n\n⏰ {timestamp}"
            
            if photo_path:
                return self._send_photo(full_message, photo_path)
            else:
                return self._send_message(full_message)
        
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False
    
    def _send_message(self, text):
        """Send text message"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": self.chat_id, "text": text}
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _send_photo(self, caption, photo_path):
        """Send photo with caption"""
        try:
            url = f"{self.base_url}/sendPhoto"
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': self.chat_id, 'caption': caption}
                response = requests.post(url, data=data, files=files, timeout=15)
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Photo send failed: {e}")
            return False


telegram_notifier = TelegramNotifier()


def send_alert(message, photo_path=None):
    """Quick function"""
    return telegram_notifier.send_alert(message, photo_path)


def is_configured():
    """Check if configured"""
    return telegram_notifier.is_configured()