"""
Ollama Client - Optimized
Auto ON/OFF | Professional Code | Auto-Save | No Comments
"""

import requests
import subprocess
import time
import re
import os
import psutil
from datetime import datetime
from pathlib import Path
from config import Config
from src.utils.logger import Logger

logger = Logger.get_logger("Ollama")


class OllamaClient:
    """Optimized Ollama for professional code generation"""
    
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self.is_running = False
        self.save_dir = Path("generated_codes")
        self.save_dir.mkdir(exist_ok=True)
    
    def _check_running(self):
        """Quick health check"""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=1)
            return r.status_code == 200
        except:
            return False
    
    def _start(self):
        """Start Ollama silently"""
        if self._check_running():
            self.is_running = True
            logger.info("Ollama ready")
            return True
        
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            time.sleep(3)
            self.is_running = self._check_running()
            if self.is_running:
                logger.info("Ollama started")
            return self.is_running
        except Exception as e:
            logger.error(f"Start failed: {e}")
            return False
    
    def _stop(self):
        """Kill all Ollama processes - frees 4-6GB RAM"""
        try:
            killed = 0
            for proc in psutil.process_iter(['name']):
                if 'ollama' in proc.info['name'].lower():
                    proc.kill()
                    killed += 1
            
            if killed:
                self.is_running = False
                logger.info(f"Stopped {killed} process(es) - RAM freed")
            return killed > 0
        except Exception as e:
            logger.error(f"Stop failed: {e}")
            return False
    
    def generate_code(self, prompt, language="python"):
        """
        Generate professional code
        Returns: {code, language, filepath, error}
        """
        try:
            if not self.is_running and not self._start():
                return {"error": "Ollama not available", "code": None}
            
            logger.info(f"Generating {language} code...")
            
            optimized_prompt = (
                f"Generate production-grade {language} code for: {prompt}\n\n"
                f"STRICT RULES:\n"
                f"- ZERO comments\n"
                f"- ZERO docstrings\n"
                f"- ZERO explanations\n"
                f"- Professional naming\n"
                f"- Proper indentation\n"
                f"- Best practices\n"
                f"- Clean syntax\n\n"
                f"Output ONLY executable code."
            )
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": optimized_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.85,
                        "num_predict": 1000
                    }
                },
                timeout=90
            )
            
            if response.status_code != 200:
                self._stop()
                return {"error": f"API error {response.status_code}", "code": None}
            
            raw_code = response.json().get("response", "")
            clean_code = self._extract_code(raw_code, language)
            filepath = self._save_code(clean_code, prompt, language)
            
            self._stop()
            
            logger.info(f"Code generated: {filepath}")
            
            return {
                "code": clean_code,
                "language": language,
                "filepath": str(filepath),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            self._stop()
            return {"error": str(e), "code": None}
    
    def _extract_code(self, text, lang):
        """Extract pure code, remove everything else"""
        code_block = re.search(rf"```(?:{lang})?\s*(.*?)```", text, re.DOTALL | re.I)
        code = code_block.group(1).strip() if code_block else text.strip()
        return self._strip_comments(code, lang)
    
    def _strip_comments(self, code, lang):
        """Remove all comments aggressively"""
        lines = code.split('\n')
        cleaned = []
        in_block = False
        
        for line in lines:
            s = line.strip()
            
            if not s:
                cleaned.append(line)
                continue
            
            if lang == 'python':
                if '"""' in s or "'''" in s:
                    in_block = not in_block
                    continue
                if in_block or s.startswith('#'):
                    continue
                if '#' in line and not any(q in line[:line.index('#')] for q in ['"', "'"]):
                    line = line[:line.index('#')].rstrip()
            
            elif lang in ['javascript', 'java', 'cpp', 'c', 'csharp']:
                if '/*' in s:
                    in_block = True
                if in_block:
                    if '*/' in s:
                        in_block = False
                    continue
                if '//' in line:
                    line = line[:line.index('//')].rstrip()
            
            if line.strip():
                cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def _save_code(self, code, prompt, lang):
        """Auto-save with clean filename"""
        ext_map = {
            'python': 'py', 'javascript': 'js', 'java': 'java',
            'cpp': 'cpp', 'c': 'c', 'csharp': 'cs',
            'html': 'html', 'css': 'css', 'go': 'go', 'rust': 'rs'
        }
        ext = ext_map.get(lang, 'txt')
        
        # Remove common filler words
        remove_words = [
            'write', 'code', 'for', 'create', 'make', 'generate', 'build',
            'likh', 'banao', 'bana', 'likho', 'karo',
            'python', 'javascript', 'java', 'cpp', 'html', 'css',
            'a', 'an', 'the', 'in', 'to', 'me', 'ke', 'liye', 'ka', 'ki'
        ]
        
        # Clean prompt
        name = prompt.lower()
        for word in remove_words:
            name = re.sub(rf'\b{word}\b', '', name)
        
        # Remove special chars, keep only words
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', '_', name.strip())
        name = name.strip('_')[:25]
        
        # Fallback if empty
        if not name:
            name = 'generated_code'
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.{ext}"
        filepath = self.save_dir / filename
        
        filepath.write_text(code, encoding='utf-8')
        return filepath
    
    def chat_fallback(self, message):
        """Fallback chat when Groq fails"""
        try:
            if not self.is_running and not self._start():
                return None
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"User: {message}\nAssistant (brief, 2 sentences):",
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 100}
                },
                timeout=20
            )
            
            result = response.json().get("response", "").strip() if response.status_code == 200 else None
            self._stop()
            return result
            
        except Exception as e:
            logger.error(f"Chat fallback failed: {e}")
            self._stop()
            return None
    
    def stop(self):
        """Manual stop"""
        self._stop()