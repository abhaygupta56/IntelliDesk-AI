"""
src/core/context_manager.py
Conversation Context Manager - Tracks last N messages
"""

from collections import deque
from src.utils.logger import Logger

logger = Logger.get_logger("ContextManager")


class ContextManager:
    """
    Stores conversation history for context-aware responses
    """
    
    def __init__(self, max_history=5):
        self.history = deque(maxlen=max_history)
        self.last_intent = None
        self.last_params = {}
        self.last_result = None
    
    def add(self, role, message, intent=None, params=None, result=None):
        """
        Add message to history
        
        Args:
            role: "user" or "assistant"
            message: The message text
            intent: Detected intent (for user messages)
            params: Extracted params (for user messages)
            result: Execution result (for assistant messages)
        """
        entry = {
            "role": role,
            "message": message,
            "intent": intent,
            "params": params,
            "result": result
        }
        
        self.history.append(entry)
        
        # Track last user intent for context reference
        if role == "user" and intent:
            self.last_intent = intent
            self.last_params = params or {}
        
        if role == "assistant" and result:
            self.last_result = result
    
    def get_history(self):
        """Get full history as list"""
        return list(self.history)
    
    def get_last_user_message(self):
        """Get last user message"""
        for entry in reversed(self.history):
            if entry["role"] == "user":
                return entry
        return None
    
    def get_last_intent(self):
        """Get last detected intent"""
        return self.last_intent
    
    def get_last_params(self):
        """Get last extracted params"""
        return self.last_params
    
    def get_last_result(self):
        """Get last execution result"""
        return self.last_result
    
    def has_context_reference(self, command):
        """
        Check if command references previous context
        
        Returns:
            dict: {"has_ref": bool, "ref_type": str, "resolved": str}
        """
        command_lower = command.lower()
        
        # Context reference words
        CONTEXT_WORDS = {
            # Hindi/Hinglish
            "usme": "in_it",
            "uspe": "on_it", 
            "usse": "from_it",
            "isme": "in_this",
            "ispe": "on_this",
            "isse": "from_this",
            "waha": "there",
            "yaha": "here",
            "wahi": "same",
            "usi": "same",
            "usko": "to_it",
            "uska": "its",
            
            # English
            "it": "it",
            "that": "that",
            "there": "there",
            "same": "same",
            "this": "this",
        }
        
        for word, ref_type in CONTEXT_WORDS.items():
            if word in command_lower.split():
                return {
                    "has_ref": True,
                    "ref_type": ref_type,
                    "word": word,
                    "last_intent": self.last_intent,
                    "last_params": self.last_params
                }
        
        return {"has_ref": False}
    
    def resolve_context(self, command, intent_data):
        """
        Resolve context references in command
        
        Example:
            Last: "open youtube"
            Current: "usme lofi search kar"
            Resolved: intent=youtube_search, params={query: "lofi"}
        """
        context_check = self.has_context_reference(command)
        
        if not context_check["has_ref"]:
            return intent_data
        
        if not self.last_intent:
            return intent_data
        
        # Context resolution rules
        resolved = intent_data.copy()
        
        # Rule 1: "usme search" after "open youtube" → youtube_search
        if self.last_intent in ["web_open", "app_open"]:
            last_target = self.last_params.get("url") or self.last_params.get("app")
            
            if last_target and "youtube" in str(last_target).lower():
                if intent_data.get("intent") == "web_search":
                    resolved["intent"] = "youtube_search"
                    resolved["context_resolved"] = True
                    logger.info(f"Context resolved: web_search → youtube_search")
        
        # Rule 2: "usme stackoverflow khol" after "open chrome" → web_open
        if self.last_intent == "app_open":
            if intent_data.get("intent") == "web_open":
                resolved["context_resolved"] = True
                logger.info("Context resolved: web_open in opened browser")
        
        # Rule 3: "usi ko bhej" after whatsapp → same recipient
        if self.last_intent == "whatsapp":
            if intent_data.get("intent") == "whatsapp":
                if not intent_data.get("params", {}).get("recipient"):
                    resolved["params"] = resolved.get("params", {})
                    resolved["params"]["recipient"] = self.last_params.get("recipient")
                    resolved["context_resolved"] = True
                    logger.info(f"Context resolved: same recipient {self.last_params.get('recipient')}")
        
        return resolved
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.last_intent = None
        self.last_params = {}
        self.last_result = None
    
    def get_groq_context(self):
        """Get history formatted for Groq API"""
        formatted = []
        for entry in self.history:
            formatted.append({
                "role": entry["role"],
                "message": entry["message"]
            })
        return formatted


# Singleton
context = ContextManager()

def add_user(message, intent=None, params=None):
    """Add user message"""
    context.add("user", message, intent, params)

def add_assistant(message, result=None):
    """Add assistant message"""
    context.add("assistant", message, result=result)

def get_history():
    """Get history"""
    return context.get_history()

def has_context_ref(command):
    """Check for context reference"""
    return context.has_context_reference(command)

def resolve(command, intent_data):
    """Resolve context"""
    return context.resolve_context(command, intent_data)

def get_last():
    """Get last intent and params"""
    return {
        "intent": context.last_intent,
        "params": context.last_params,
        "result": context.last_result
    }

def clear():
    """Clear history"""
    context.clear()

def get_groq_context():
    """Get formatted context for Groq"""
    return context.get_groq_context()