"""
Configuration Manager for IntelliDesk AI
Centralized settings with validation
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application Configuration"""
    
    # ═══════════════════════════════════════════════════════════════════
    # PATHS
    # ═══════════════════════════════════════════════════════════════════
    BASE_DIR = Path(__file__).parent  # Root directory
    SRC_DIR = BASE_DIR / "src"
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = DATA_DIR / "logs"
    
    # ═══════════════════════════════════════════════════════════════════
    # API KEYS
    # ═══════════════════════════════════════════════════════════════════
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # ═══════════════════════════════════════════════════════════════════
    # GROQ SETTINGS
    # ═══════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════

    GROQ_MODEL = "llama-3.1-8b-instant"  # Fast, free-tier friendly
    GROQ_MAX_REQUESTS_PER_MINUTE = int(os.getenv("GROQ_MAX_REQUESTS_PER_MINUTE", "30"))
    GROQ_MAX_REQUESTS_PER_DAY = int(os.getenv("GROQ_MAX_REQUESTS_PER_DAY", "14400"))
    
    # ═══════════════════════════════════════════════════════════════════
    # OLLAMA SETTINGS (Fallback + Code Generation)
    # ═══════════════════════════════════════════════════════════════════
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
    
    # ═══════════════════════════════════════════════════════════════════
    # EMAIL SETTINGS
    # ═══════════════════════════════════════════════════════════════════
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    # Telegram Configuration (for Sentry Mode)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    # ═══════════════════════════════════════════════════════════════════
    # APP SETTINGS
    # ═══════════════════════════════════════════════════════════════════
    APP_NAME = "IntelliDesk AI"
    APP_VERSION = "2.0.0"
    LANGUAGE = os.getenv("LANGUAGE", "auto")  # auto, en, hi
    
    # Voice
    VOICE_ENABLED = os.getenv("VOICE_ENABLED", "false").lower() == "true"
    VOICE_RATE = int(os.getenv("VOICE_RATE", "150"))
    
    # ═══════════════════════════════════════════════════════════════════
    # DATABASE
    # ═══════════════════════════════════════════════════════════════════
    DATABASE_PATH = DATA_DIR / "intellidesk.db"
    
    # ═══════════════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════════════
    LOG_FILE = LOG_DIR / "app.log"
    ERROR_LOG_FILE = LOG_DIR / "error.log"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # ═══════════════════════════════════════════════════════════════════
    # VALIDATION & INITIALIZATION
    # ═══════════════════════════════════════════════════════════════════
    
    @classmethod
    def validate(cls):
        """Validate critical settings and create directories"""
        errors = []
        warnings = []
        
        # Check Groq API key
        if not cls.GROQ_API_KEY:
            errors.append("❌ GROQ_API_KEY not found in .env file")
        
        # Check email config (optional)
        if not cls.EMAIL_ADDRESS or not cls.EMAIL_PASSWORD:
            warnings.append("⚠️  Email not configured (email features disabled)")
        
        # Create directories
        try:
            cls.DATA_DIR.mkdir(exist_ok=True)
            cls.LOG_DIR.mkdir(exist_ok=True)
        except Exception as e:
            errors.append(f"❌ Failed to create directories: {e}")
        
        # Print results
        if errors:
            print("\n" + "="*60)
            print("CONFIGURATION ERRORS:")
            print("="*60)
            for error in errors:
                print(error)
            print("="*60 + "\n")
            raise ValueError("Configuration validation failed")
        
        if warnings:
            print("\n" + "="*60)
            print("CONFIGURATION WARNINGS:")
            print("="*60)
            for warning in warnings:
                print(warning)
            print("="*60 + "\n")
        
        return True
    
    @classmethod
    def get_info(cls):
        """Get configuration summary"""
        return {
            "app_name": cls.APP_NAME,
            "version": cls.APP_VERSION,
            "groq_configured": bool(cls.GROQ_API_KEY),
            "groq_model": cls.GROQ_MODEL,
            "ollama_url": cls.OLLAMA_BASE_URL,
            "ollama_model": cls.OLLAMA_MODEL,
            "email_configured": bool(cls.EMAIL_ADDRESS and cls.EMAIL_PASSWORD),
            "voice_enabled": cls.VOICE_ENABLED,
            "database": str(cls.DATABASE_PATH),
        }
    
    @classmethod
    def print_info(cls):
        """Print configuration info (for debugging)"""
        print("\n" + "="*60)
        print(f"⚙️  {cls.APP_NAME} v{cls.APP_VERSION} - Configuration")
        print("="*60)
        info = cls.get_info()
        for key, value in info.items():
            print(f"  {key:20s}: {value}")
        print("="*60 + "\n")


# Auto-validate on import
try:
    Config.validate()
except ValueError as e:
    print(f"\n⚠️  Fix your .env file and restart.\n")
    import sys
    sys.exit(1)


# Export for convenience
GROQ_API_KEY = Config.GROQ_API_KEY
OLLAMA_BASE_URL = Config.OLLAMA_BASE_URL
OLLAMA_MODEL = Config.OLLAMA_MODEL