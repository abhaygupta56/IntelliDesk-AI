"""
Web Operations Module
Features:
- Google search
- YouTube search/play
- Open websites
- Wikipedia search
- Download files
- URL shortener
- Weather info
"""

import webbrowser
import urllib.parse
import requests
from pathlib import Path
from datetime import datetime
from src.utils.logger import Logger
from src.database.db_manager import DatabaseManager

logger = Logger.get_logger("WebOps")


class WebAutomation:
    """Web operations handler"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_history()
    
    def _init_history(self):
        """Track web operations"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS web_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    query TEXT,
                    url TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create web history: {e}")
    
    def google_search(self, query: str):
        """Search on Google"""
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded}"
            
            webbrowser.open(url)
            self._save_history("google_search", query, url)
            
            logger.info(f"✅ Google search: {query}")
            
            return {
                "status": "success",
                "message": f"Searching Google for: {query}",
                "data": {"query": query, "url": url}
            }
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def youtube_search(self, query: str):
        """Search on YouTube"""
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded}"
            
            webbrowser.open(url)
            self._save_history("youtube_search", query, url)
            
            logger.info(f"✅ YouTube search: {query}")
            
            return {
                "status": "success",
                "message": f"Searching YouTube for: {query}",
                "data": {"query": query, "url": url}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def youtube_play(self, query: str):
        """Play first YouTube result"""
        try:
            import pywhatkit as kit
            kit.playonyt(query)
            
            self._save_history("youtube_play", query, "")
            logger.info(f"✅ Playing on YouTube: {query}")
            
            return {
                "status": "success",
                "message": f"Playing: {query}"
            }
        except Exception as e:
            # Fallback to search
            return self.youtube_search(query)
    
    def open_website(self, url: str):
        """Open website"""
        try:
            # Add https if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            self._save_history("open_website", "", url)
            
            logger.info(f"✅ Opened: {url}")
            
            return {
                "status": "success",
                "message": f"Opened {url}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def wikipedia_search(self, query: str):
        """Search Wikipedia"""
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://en.wikipedia.org/wiki/{encoded}"
            
            webbrowser.open(url)
            self._save_history("wikipedia", query, url)
            
            logger.info(f"✅ Wikipedia: {query}")
            
            return {
                "status": "success",
                "message": f"Opened Wikipedia: {query}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_weather(self, city: str = ""):
        """Get weather info"""
        try:
            if city:
                url = f"https://wttr.in/{city}?format=3"
                web_url = f"https://www.google.com/search?q=weather+{city}"
            else:
                url = "https://wttr.in/?format=3"
                web_url = "https://www.google.com/search?q=weather"
            
            # Get text weather
            try:
                response = requests.get(url, timeout=5)
                weather_text = response.text.strip()
            except:
                weather_text = None
            
            # Also open in browser
            webbrowser.open(web_url)
            
            logger.info(f"✅ Weather: {city or 'current location'}")
            
            return {
                "status": "success",
                "message": weather_text or f"Weather for {city}",
                "data": {"city": city, "weather": weather_text}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def download_file(self, url: str, filename: str = None):
        """Download file from URL"""
        try:
            # Default download folder
            download_folder = Path.home() / "Downloads"
            
            # Get filename from URL if not provided
            if not filename:
                filename = url.split('/')[-1].split('?')[0]
                if not filename:
                    filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            filepath = download_folder / filename
            
            logger.info(f"Downloading: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self._save_history("download", filename, url)
            logger.info(f"✅ Downloaded: {filename}")
            
            return {
                "status": "success",
                "message": f"Downloaded: {filename}",
                "data": {"path": str(filepath), "filename": filename}
            }
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _save_history(self, operation: str, query: str, url: str):
        """Save to history"""
        try:
            conn = self.db.get_connection()
            conn.execute(
                "INSERT INTO web_history (operation, query, url) VALUES (?, ?, ?)",
                (operation, query, url)
            )
            conn.commit()
        except:
            pass


# Common websites shortcuts
WEBSITE_SHORTCUTS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://www.github.com",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
}


# Global instance
_web = WebAutomation()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def google(query):
    """Google search"""
    return _web.google_search(query)

def youtube(query):
    """YouTube search"""
    return _web.youtube_search(query)

def play(query):
    """Play on YouTube"""
    return _web.youtube_play(query)

def open_website(url):
    """Open website"""
    # Check shortcuts first
    url_lower = url.lower().strip()
    if url_lower in WEBSITE_SHORTCUTS:
        url = WEBSITE_SHORTCUTS[url_lower]
    
    return _web.open_website(url)

def wikipedia(query):
    """Wikipedia search"""
    return _web.wikipedia_search(query)

def weather(city=""):
    """Get weather"""
    return _web.get_weather(city)

def download(url, filename=None):
    """Download file"""
    return _web.download_file(url, filename)