"""
Groq API Client with Hinglish support
"""

from groq import Groq
from config import Config
from src.utils.logger import Logger
from src.database.db_manager import DatabaseManager

logger = Logger.get_logger("Groq")
db = DatabaseManager()

class GroqClient:
    """Groq API wrapper with rate limiting and Hinglish support"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"  # Fast model for chat
    
    def check_rate_limit(self):
        """Check if we've hit rate limits"""
        usage = db.get_api_usage_today("groq")
        
        if usage["requests"] >= Config.GROQ_MAX_REQUESTS_PER_DAY:
            logger.warning("Daily Groq limit reached")
            return False
        
        return True
    
    def chat(self, message, context=None):
        """
        Send chat message to Groq (supports English + Hinglish)
        
        Args:
            message: User message
            context: Previous conversation context
        
        Returns:
            dict: {response, tokens, model, error}
        """
        try:
            # Check rate limit
            if not self.check_rate_limit():
                return {
                    "response": None,
                    "error": "rate_limit",
                    "tokens": 0
                }
            
            # Build messages
            messages = []
            
            # System prompt (supports Hinglish)
            system_prompt = """You are a helpful AI assistant. 
Give SHORT, concise responses (2-3 sentences max). 
You can respond in English or Hinglish (Hindi+English mix). 
Match the user's language style.
Only give detailed explanations when explicitly asked with 'explain' or 'samjhao'. 
Be casual and friendly."""
            
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            # Add context if provided
            if context:
                for msg in context[-5:]:  # Last 5 messages
                    messages.append({
                        "role": msg["role"],
                        "content": msg["message"]
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,  # Short responses
                top_p=1,
                stream=False
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Log usage
            db.log_api_usage("groq", tokens_used)
            
            logger.info(f"Groq response: {tokens_used} tokens")
            
            return {
                "response": ai_response,
                "tokens": tokens_used,
                "model": self.model,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {
                "response": None,
                "error": str(e),
                "tokens": 0
            }
    
    def chat_detailed(self, message, context=None):
        """Chat with detailed response (for 'explain' or 'samjhao' queries)"""
        try:
            if not self.check_rate_limit():
                return {
                    "response": None,
                    "error": "rate_limit",
                    "tokens": 0
                }
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Provide detailed, comprehensive explanations. You can use English or Hinglish based on user's preference."
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800,  # Longer for explanations
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            db.log_api_usage("groq", tokens_used)
            
            logger.info(f"Groq detailed response: {tokens_used} tokens")
            
            return {
                "response": ai_response,
                "tokens": tokens_used,
                "model": self.model,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Groq detailed API error: {e}")
            return {
                "response": None,
                "error": str(e),
                "tokens": 0
            }