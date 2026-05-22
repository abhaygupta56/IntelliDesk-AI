"""
Conversation Manager - The Brain
Routes all user input through Groq LLM with function calling
WITH DEBUG TIMING TO FIND SLOW CODE
"""

import time
from src.core.groq_assistant import GroqAssistant
from src.core.function_registry import registry
from src.utils.logger import Logger

logger = Logger.get_logger("ConversationManager")


class ConversationManager:
    """
    Manages conversation flow and routes to appropriate handlers
    """
    
    def __init__(self):
        self.groq = GroqAssistant()
        self.conversation_history = []
    
    def process(self, user_input: str):
        """
        Main entry point - processes any user input
        WITH DETAILED TIMING DEBUG
        """
        overall_start = time.time()
        
        try:
            user_input = user_input.strip()
            
            if not user_input:
                return [{
                    "type": "error",
                    "response": "Please say something!",
                    "status": "error"
                }]
            
            logger.info(f"Processing: {user_input}")
            
            # ════════════════════════════════════════════════════════════
            # TIMING: Code generation check
            # ════════════════════════════════════════════════════════════
            t1 = time.time()
            is_code = self._is_code_request(user_input)
            logger.info(f"⏱️  _is_code_request(): {time.time()-t1:.4f}s")
            
            if is_code:
                result = self._handle_code_generation(user_input)
                logger.info(f"⏱️  TOTAL: {time.time()-overall_start:.2f}s (code gen)")
                return [result]
            
            # ════════════════════════════════════════════════════════════
            # TIMING: Split commands check
            # ════════════════════════════════════════════════════════════
            t2 = time.time()
            commands = self._split_commands(user_input)
            logger.info(f"⏱️  _split_commands(): {time.time()-t2:.4f}s (found {len(commands)})")
            
            if len(commands) > 1:
                logger.info(f"Multi-step: {len(commands)} steps")
                result = self._process_multi_step(commands)
                logger.info(f"⏱️  TOTAL: {time.time()-overall_start:.2f}s (multi-step)")
                return result
            
            # ════════════════════════════════════════════════════════════
            # TIMING: Groq chat call (THIS SHOULD BE ~0.5s)
            # ════════════════════════════════════════════════════════════
            t3 = time.time()
            result = self.groq.chat(user_input)
            logger.info(f"⏱️  self.groq.chat(): {time.time()-t3:.2f}s")
            
            # ════════════════════════════════════════════════════════════
            # TIMING: Save to history
            # ════════════════════════════════════════════════════════════
            t4 = time.time()
            self._add_to_history("user", user_input)
            self._add_to_history("assistant", result.get("response", ""))
            logger.info(f"⏱️  _add_to_history(): {time.time()-t4:.4f}s")
            
            # ════════════════════════════════════════════════════════════
            # TIMING: Total
            # ════════════════════════════════════════════════════════════
            logger.info(f"⏱️  ═══ TOTAL process(): {time.time()-overall_start:.2f}s ═══")
            
            return [result]
        
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            logger.info(f"⏱️  TOTAL (error): {time.time()-overall_start:.2f}s")
            return [{
                "type": "error",
                "response": f"Something went wrong: {str(e)}",
                "status": "error"
            }]
    
    def _split_commands(self, text: str):
        """
        Split multi-step commands
        """
        import re
        
        # Simple word-based connectors ONLY
        simple_connectors = [
            r'\s+then\s+',
            r'\s+phir\s+',
            r'\s+fir\s+',
            r'\s+uske baad\s+',
            r'\s+iske baad\s+',
            r'\s+baad mein\s+',
            r'\s+baad me\s+',
            r'\s+and then\s+',
            r'\s+after that\s+',
            r'\s+aur phir\s+',
            r'\s+toh phir\s+',
        ]
        
        # Create pattern
        pattern = '|'.join(simple_connectors)
        
        # Split
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        # Clean
        commands = [p.strip() for p in parts if p and p.strip()]
        
        if len(commands) > 1:
            logger.info(f"Split into {len(commands)} commands: {commands}")
            return commands
        
        return [text]
    
    def _process_multi_step(self, commands: list):
        """Process multiple commands in sequence"""
        results = []
        
        for i, cmd in enumerate(commands, 1):
            t_step = time.time()
            logger.info(f"Step {i}/{len(commands)}: {cmd}")
            
            result = self.groq.chat(cmd)
            results.append(result)
            
            logger.info(f"⏱️  Step {i} groq.chat(): {time.time()-t_step:.2f}s")
            
            # Save to history
            self._add_to_history("user", cmd)
            self._add_to_history("assistant", result.get("response", ""))
            
            # Stop on error
            if result.get("status") in ["error", "needs_info"]:
                break
        
        return results
    
    def _is_code_request(self, text: str):
        """Detect code generation requests"""
        raw = text.lower()
        
        # Exclude questions/informational requests that don't command action
        question_words = ["which", "why", "who", "where", "recommend", "suggest", "compare", "difference", "how"]
        is_question = any(q in raw for q in question_words) or (raw.startswith("what ") and not any(v in raw for v in ["write", "generate", "create", "make", "build"]))
        if is_question and not any(verb in raw for verb in ["write", "generate", "create", "make", "build", "implement"]):
            return False
            
        # 1. Regex patterns for flexible matching
        code_indicators = [
            r"\b(write|generate|create|make|build)\b.*\b(code|script|program|function|algorithm|app|class|macro)\b",
            r"\b(code|script|program|function)\b.*\b(for|to|of|that)\b",
            r"\b(write|generate|create)\b.*\b(python|javascript|java|cpp|html|css|bash|powershell|sql|c#)\b",
            r"\b(python|javascript|cpp|java|c#|html)\b.*\b(code|script|program|function|implementation)\b",
            r"\b(code\s+(likh|likho|banao|generate\s+karo))\b",
            r"\b(script\s+(bana|banao|likh|likho))\b",
            r"\b(write|generate|create|make|build|code|script|program)\b.*\b(in|on)\b.*\b(vscode|notepad|sublime|eclipse|pycharm|visual studio)\b",
        ]
        
        import re
        for pattern in code_indicators:
            if re.search(pattern, raw):
                return True
                
        # 2. String fallbacks
        code_keywords = [
            "write code", "generate code", "code likh", "code likho", "script bana",
            "program likh", "write a script", "create a program", "write python",
            "write javascript", "create script", "make a program", "code banao",
            "write a code", "generate a code", "write program", "generate program"
        ]
        return any(keyword in raw for keyword in code_keywords)
    
    def _handle_code_generation(self, prompt: str):
        """Route to Ollama for code generation with auto-save"""
        try:
            from src.llm.ollama_client import OllamaClient
            
            language = self._detect_language(prompt)
            logger.info(f"Code generation: {language}")
            
            ollama = OllamaClient()
            result = ollama.generate_code(prompt, language)
            
            if result.get("error"):
                return {
                    "type": "error",
                    "response": f"Code generation failed: {result['error']}",
                    "status": "error"
                }
            
            code = result.get("code", "")
            filepath = result.get("filepath", "")
            
            response_msg = (
                f"✅ Generated {language} code:\n\n"
                f"```{language}\n{code}\n```\n\n"
                f"💾 Saved to: {filepath}"
            )
            
            return {
                "type": "code_generation",
                "response": response_msg,
                "data": {
                    "code": code,
                    "language": language,
                    "filepath": filepath
                },
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Code generation error: {e}")
            return {
                "type": "error",
                "response": f"Code generation failed: {str(e)}",
                "status": "error"
            }
    
    def _detect_language(self, text: str):
        """Detect programming language from prompt"""
        text_lower = text.lower()
        
        languages = {
            "python": ["python", "py"],
            "javascript": ["javascript", "js", "node"],
            "java": ["java"],
            "cpp": ["c++", "cpp"],
            "c": ["c language", " c "],
            "csharp": ["c#", "csharp"],
            "html": ["html"],
            "css": ["css"],
        }
        
        for lang, keywords in languages.items():
            if any(kw in text_lower for kw in keywords):
                return lang
        
        return "python"
    
    def _add_to_history(self, role: str, message: str):
        """Add to conversation history"""
        self.conversation_history.append({
            "role": role,
            "message": message
        })
        
        # Keep last 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_history(self):
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.groq.reset_conversation()
        logger.info("Conversation history cleared")
    
    def get_stats(self):
        """Get usage stats"""
        return {
            "messages_in_history": len(self.conversation_history),
            "groq_history": len(self.groq.get_history())
        }


# Global instance
conversation_manager = ConversationManager()


# Convenience functions
def process(user_input: str):
    return conversation_manager.process(user_input)

def get_history():
    return conversation_manager.get_history()

def clear():
    conversation_manager.clear_history()

def stats():
    return conversation_manager.get_stats()