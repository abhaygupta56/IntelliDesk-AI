"""
Keyboard Operations Module
Features:
- Type text
- Hotkey combos
- Special keys
- Keyboard shortcuts
- Auto typing
"""

import pyautogui
import time
from src.utils.logger import Logger

logger = Logger.get_logger("Keyboard")

# Slow down pyautogui for safety
pyautogui.PAUSE = 0.1


class KeyboardManager:
    """Keyboard automation"""
    
    def type_text(self, text: str, interval: float = 0.02):
        """Type text character by character"""
        try:
            time.sleep(0.5)  # Give user time to focus
            pyautogui.typewrite(text, interval=interval)
            
            logger.info(f"Typed: {text[:30]}...")
            
            return {
                "status": "success",
                "message": f"Typed: {text[:50]}..."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def type_text_unicode(self, text: str):
        """Type text with unicode support (for non-English)"""
        try:
            import pyperclip
            
            time.sleep(0.5)
            
            # Copy to clipboard and paste
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            
            logger.info(f"Typed (unicode): {text[:30]}...")
            
            return {
                "status": "success",
                "message": f"Typed: {text[:50]}..."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def press_key(self, key: str):
        """Press a single key"""
        try:
            pyautogui.press(key)
            logger.info(f"Pressed: {key}")
            return {"status": "success", "message": f"Pressed {key}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def hotkey(self, *keys):
        """Press key combination"""
        try:
            pyautogui.hotkey(*keys)
            combo = " + ".join(keys)
            logger.info(f"Hotkey: {combo}")
            return {"status": "success", "message": f"Pressed {combo}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # Common shortcuts
    def copy(self):
        """Ctrl + C"""
        return self.hotkey('ctrl', 'c')
    
    def paste(self):
        """Ctrl + V"""
        return self.hotkey('ctrl', 'v')
    
    def cut(self):
        """Ctrl + X"""
        return self.hotkey('ctrl', 'x')
    
    def undo(self):
        """Ctrl + Z"""
        return self.hotkey('ctrl', 'z')
    
    def redo(self):
        """Ctrl + Y"""
        return self.hotkey('ctrl', 'y')
    
    def select_all(self):
        """Ctrl + A"""
        return self.hotkey('ctrl', 'a')
    
    def save(self):
        """Ctrl + S"""
        return self.hotkey('ctrl', 's')
    
    def find(self):
        """Ctrl + F"""
        return self.hotkey('ctrl', 'f')
    
    def new_tab(self):
        """Ctrl + T"""
        return self.hotkey('ctrl', 't')
    
    def close_tab(self):
        """Ctrl + W"""
        return self.hotkey('ctrl', 'w')
    
    def refresh(self):
        """F5"""
        return self.press_key('f5')
    
    def escape(self):
        """Escape"""
        return self.press_key('escape')
    
    def enter(self):
        """Enter"""
        return self.press_key('enter')
    
    def tab(self):
        """Tab"""
        return self.press_key('tab')
    
    def backspace(self):
        """Backspace"""
        return self.press_key('backspace')
    
    def delete(self):
        """Delete"""
        return self.press_key('delete')
    
    def press_enter_times(self, times: int = 1):
        """Press enter multiple times"""
        try:
            for _ in range(times):
                pyautogui.press('enter')
                time.sleep(0.1)
            return {"status": "success", "message": f"Pressed Enter {times} times"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global instance
_keyboard = KeyboardManager()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def type_text(text, interval=0.02):
    return _keyboard.type_text(text, interval)

def type_unicode(text):
    return _keyboard.type_text_unicode(text)

def press(key):
    return _keyboard.press_key(key)

def hotkey(*keys):
    return _keyboard.hotkey(*keys)

def copy():
    return _keyboard.copy()

def paste():
    return _keyboard.paste()

def cut():
    return _keyboard.cut()

def undo():
    return _keyboard.undo()

def redo():
    return _keyboard.redo()

def select_all():
    return _keyboard.select_all()

def save():
    return _keyboard.save()

def find():
    return _keyboard.find()

def new_tab():
    return _keyboard.new_tab()

def close_tab():
    return _keyboard.close_tab()

def refresh():
    return _keyboard.refresh()

def escape():
    return _keyboard.escape()

def enter(times=1):
    return _keyboard.press_enter_times(times)

def tab():
    return _keyboard.tab()

def backspace():
    return _keyboard.backspace()

def delete():
    return _keyboard.delete()