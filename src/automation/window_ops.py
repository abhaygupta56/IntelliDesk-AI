"""
Window Operations Module
Features:
- Get active window
- Minimize/Maximize
- Resize window
- Move window
- List windows
"""

import pyautogui
import pygetwindow as gw
import time
from src.utils.logger import Logger

logger = Logger.get_logger("Window")


class WindowManager:
    """Window management operations"""
    
    def get_active_window(self):
        """Get currently active window"""
        try:
            window = gw.getActiveWindow()
            
            if window:
                return {
                    "status": "success",
                    "data": {
                        "title": window.title,
                        "position": {"x": window.left, "y": window.top},
                        "size": {"width": window.width, "height": window.height}
                    }
                }
            return {"status": "error", "message": "No active window"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_windows(self):
        """List all open windows"""
        try:
            windows = gw.getAllTitles()
            # Filter empty titles
            windows = [w for w in windows if w.strip()]
            
            return {
                "status": "success",
                "windows": windows,
                "count": len(windows)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def find_window(self, title: str):
        """Find window by title"""
        try:
            windows = gw.getWindowsWithTitle(title)
            
            if windows:
                window = windows[0]
                return {
                    "status": "success",
                    "data": {
                        "title": window.title,
                        "position": {"x": window.left, "y": window.top},
                        "size": {"width": window.width, "height": window.height}
                    }
                }
            return {"status": "error", "message": f"Window '{title}' not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def activate_window(self, title: str):
        """Bring window to foreground"""
        try:
            windows = gw.getWindowsWithTitle(title)
            
            if windows:
                window = windows[0]
                window.activate()
                time.sleep(0.3)
                
                logger.info(f"Activated window: {title}")
                return {"status": "success", "message": f"Activated: {window.title}"}
            
            return {"status": "error", "message": f"Window '{title}' not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def minimize_window(self, title: str = None):
        """Minimize window"""
        try:
            if title:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].minimize()
                    logger.info(f"Minimized: {title}")
                    return {"status": "success", "message": f"Minimized: {title}"}
                return {"status": "error", "message": f"Window '{title}' not found"}
            else:
                # Minimize active window
                window = gw.getActiveWindow()
                if window:
                    window.minimize()
                    logger.info(f"Minimized active window")
                    return {"status": "success", "message": "Window minimized"}
                return {"status": "error", "message": "No active window"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def maximize_window(self, title: str = None):
        """Maximize window"""
        try:
            if title:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].maximize()
                    logger.info(f"Maximized: {title}")
                    return {"status": "success", "message": f"Maximized: {title}"}
                return {"status": "error", "message": f"Window '{title}' not found"}
            else:
                window = gw.getActiveWindow()
                if window:
                    window.maximize()
                    logger.info(f"Maximized active window")
                    return {"status": "success", "message": "Window maximized"}
                return {"status": "error", "message": "No active window"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def close_window(self, title: str = None):
        """Close window"""
        try:
            if title:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].close()
                    logger.info(f"Closed: {title}")
                    return {"status": "success", "message": f"Closed: {title}"}
                return {"status": "error", "message": f"Window '{title}' not found"}
            else:
                window = gw.getActiveWindow()
                if window:
                    window.close()
                    return {"status": "success", "message": "Window closed"}
                return {"status": "error", "message": "No active window"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def resize_window(self, width: int, height: int, title: str = None):
        """Resize window"""
        try:
            if title:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].resizeTo(width, height)
                    return {"status": "success", "message": f"Resized to {width}x{height}"}
                return {"status": "error", "message": f"Window '{title}' not found"}
            else:
                window = gw.getActiveWindow()
                if window:
                    window.resizeTo(width, height)
                    return {"status": "success", "message": f"Resized to {width}x{height}"}
                return {"status": "error", "message": "No active window"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def move_window(self, x: int, y: int, title: str = None):
        """Move window to position"""
        try:
            if title:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].moveTo(x, y)
                    return {"status": "success", "message": f"Moved to ({x}, {y})"}
                return {"status": "error", "message": f"Window '{title}' not found"}
            else:
                window = gw.getActiveWindow()
                if window:
                    window.moveTo(x, y)
                    return {"status": "success", "message": f"Moved to ({x}, {y})"}
                return {"status": "error", "message": "No active window"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global instance
_window = WindowManager()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_active():
    return _window.get_active_window()

def list_windows():
    return _window.list_windows()

def find(title):
    return _window.find_window(title)

def activate(title):
    return _window.activate_window(title)

def minimize(title=None):
    return _window.minimize_window(title)

def maximize(title=None):
    return _window.maximize_window(title)

def close(title=None):
    return _window.close_window(title)

def resize(width, height, title=None):
    return _window.resize_window(width, height, title)

def move(x, y, title=None):
    return _window.move_window(x, y, title)