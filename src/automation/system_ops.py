"""
System Operations Module - Advanced
Features:
- Smart app launch (via Start Menu search)
- Screenshot (full/region/window)
- Volume/Brightness control
- System info
- Clipboard operations
- Lock/Shutdown/Restart/Sleep
"""

import os
import time
import psutil
import pyautogui
import pyperclip
import subprocess
from datetime import datetime
from pathlib import Path
from src.utils.logger import Logger
from src.database.db_manager import DatabaseManager

logger = Logger.get_logger("System")

# Disable pyautogui fail-safe for smoother operation
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3


class AppManager:
    """Smart App Management via Start Menu"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_app_history()
    
    def _init_app_history(self):
        """Track app usage"""
        try:
            conn = self.db.get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    action TEXT DEFAULT 'open',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to create app history: {e}")
    
    def open_app(self, app_name):
        """
        Open app via Start Menu search (Windows key + type + enter)
        Works with ANY app - no restrictions!
        """
        try:
            logger.info(f"Opening app: {app_name}")
            
            # Handle Chrome specifically to bypass profile picker
            if app_name.lower().strip() in ["chrome", "google chrome"]:
                os.system('start chrome --profile-directory="Default"')
                self._save_history(app_name, 'open')
                logger.info(f"✅ App launched: {app_name} (Default Profile)")
                return {
                    "status": "success",
                    "message": f"{app_name} opened",
                    "data": {"app": app_name, "method": "direct_command"}
                }
            
            # Press Windows key to open Start Menu
            pyautogui.press('win')
            time.sleep(0.5)
            
            # Type app name
            pyautogui.typewrite(app_name, interval=0.05)
            time.sleep(0.8)
            
            # Press Enter to launch
            pyautogui.press('enter')
            time.sleep(0.3)
            
            # Save to history
            self._save_history(app_name, 'open')
            
            logger.info(f"[OK] App launched: {app_name}")
            
            return {
                "status": "success",
                "message": f"{app_name} opened",
                "data": {"app": app_name, "method": "start_menu"}
            }
            
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {str(e)}")
            return {"status": "error", "message": f"Failed to open {app_name}: {str(e)}"}
    
    def close_app(self, app_name):
        """Close app by name using Alt+F4 or taskkill"""
        try:
            logger.info(f"Closing app: {app_name}")
            
            # Common app process names
            process_map = {
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "notepad": "notepad.exe",
                "word": "WINWORD.EXE",
                "excel": "EXCEL.EXE",
                "powerpoint": "POWERPNT.EXE",
                "vscode": "Code.exe",
                "vs code": "Code.exe",
                "spotify": "Spotify.exe",
                "discord": "Discord.exe",
                "telegram": "Telegram.exe",
                "whatsapp": "WhatsApp.exe",
                "vlc": "vlc.exe",
                "calculator": "Calculator.exe",
                "calc": "Calculator.exe",
            }
            
            process_name = process_map.get(app_name.lower(), f"{app_name}.exe")
            
            # Try to kill process
            killed = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    killed = True
            
            if killed:
                self._save_history(app_name, 'close')
                logger.info(f"✅ App closed: {app_name}")
                return {"status": "success", "message": f"{app_name} closed"}
            else:
                # Fallback: taskkill via subprocess (list args = no shell injection)
                subprocess.run(
                    ['taskkill', '/IM', process_name, '/F'],
                    capture_output=True
                )
                return {"status": "success", "message": f"Attempted to close {app_name}"}
                
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def minimize_all(self):
        """Minimize all windows (Win + D)"""
        try:
            pyautogui.hotkey('win', 'd')
            logger.info("All windows minimized")
            return {"status": "success", "message": "All windows minimized"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def switch_window(self):
        """Switch to next window (Alt + Tab)"""
        try:
            pyautogui.hotkey('alt', 'tab')
            return {"status": "success", "message": "Switched window"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _save_history(self, app_name, action):
        """Save app action to history"""
        try:
            conn = self.db.get_connection()
            conn.execute(
                "INSERT INTO app_history (app_name, action) VALUES (?, ?)",
                (app_name, action)
            )
            conn.commit()
        except Exception:
            pass


class ScreenshotManager:
    """Handle screenshots"""
    
    def __init__(self):
        self.default_folder = Path.home() / "Pictures" / "IntelliDesk_Screenshots"
        self.default_folder.mkdir(parents=True, exist_ok=True)
    
    def take_full(self, filename=None):
        """Take full screen screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = self.default_folder / filename
            
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            
            logger.info(f"✅ Screenshot saved: {filepath}")
            
            return {
                "status": "success",
                "message": f"Screenshot saved",
                "data": {"path": str(filepath), "filename": filename}
            }
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def take_region(self, x, y, width, height, filename=None):
        """Take screenshot of specific region"""
        try:
            if not filename:
                filename = f"region_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = self.default_folder / filename
            
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(str(filepath))
            
            logger.info(f"✅ Region screenshot saved: {filepath}")
            
            return {
                "status": "success",
                "message": "Region screenshot saved",
                "data": {"path": str(filepath)}
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def take_window(self, filename=None):
        """Take screenshot of active window"""
        try:
            if not filename:
                filename = f"window_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = self.default_folder / filename
            
            # Alt + PrtScn for active window
            pyautogui.hotkey('alt', 'printscreen')
            time.sleep(0.3)
            
            # Get from clipboard
            from PIL import ImageGrab
            screenshot = ImageGrab.grabclipboard()
            
            if screenshot:
                screenshot.save(str(filepath))
                logger.info(f"✅ Window screenshot saved: {filepath}")
                return {
                    "status": "success",
                    "message": "Window screenshot saved",
                    "data": {"path": str(filepath)}
                }
            else:
                # Fallback to full screenshot
                return self.take_full(filename)
                
        except Exception as e:
            return {"status": "error", "message": str(e)}


class VolumeControl:
    """System volume control"""
    
    def volume_up(self, steps=5):
        """Increase volume"""
        try:
            for _ in range(steps):
                pyautogui.press('volumeup')
            
            logger.info(f"Volume increased by {steps * 2}%")
            return {"status": "success", "message": f"Volume increased"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def volume_down(self, steps=5):
        """Decrease volume"""
        try:
            for _ in range(steps):
                pyautogui.press('volumedown')
            
            logger.info(f"Volume decreased by {steps * 2}%")
            return {"status": "success", "message": f"Volume decreased"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def mute(self):
        """Toggle mute"""
        try:
            pyautogui.press('volumemute')
            logger.info("Volume muted/unmuted")
            return {"status": "success", "message": "Volume muted/unmuted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class BrightnessControl:
    """Screen brightness control (Windows)"""
    
    def brightness_up(self, steps=10):
        """Increase brightness"""
        try:
            # Using PowerShell to adjust brightness
            current = self._get_brightness()
            new_value = min(100, current + steps)
            self._set_brightness(new_value)
            
            logger.info(f"Brightness set to {new_value}%")
            return {"status": "success", "message": f"Brightness increased to {new_value}%"}
        except Exception as e:
            # Fallback - keyboard shortcut (some laptops)
            try:
                for _ in range(steps // 10):
                    pyautogui.hotkey('fn', 'f12')  # Common brightness up key
                return {"status": "success", "message": "Brightness increased"}
            except Exception:
                return {"status": "error", "message": str(e)}
    
    def brightness_down(self, steps=10):
        """Decrease brightness"""
        try:
            current = self._get_brightness()
            new_value = max(0, current - steps)
            self._set_brightness(new_value)
            
            logger.info(f"Brightness set to {new_value}%")
            return {"status": "success", "message": f"Brightness decreased to {new_value}%"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _get_brightness(self):
        """Get current brightness"""
        try:
            import screen_brightness_control as sbc
            return sbc.get_brightness()[0]
        except Exception:
            return 50  # Default assumption
    
    def _set_brightness(self, value):
        """Set brightness value"""
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(value)
        except Exception:
            # PowerShell fallback
            cmd = f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{value})'
            subprocess.run(['powershell', '-Command', cmd], capture_output=True)


class ClipboardManager:
    """Clipboard operations"""
    
    def copy(self, text):
        """Copy text to clipboard"""
        try:
            pyperclip.copy(text)
            logger.info(f"Copied to clipboard: {text[:50]}...")
            return {"status": "success", "message": "Copied to clipboard"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def paste(self):
        """Get clipboard content"""
        try:
            content = pyperclip.paste()
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def paste_action(self):
        """Perform paste action (Ctrl+V)"""
        try:
            pyautogui.hotkey('ctrl', 'v')
            return {"status": "success", "message": "Pasted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def copy_action(self):
        """Perform copy action (Ctrl+C)"""
        try:
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.1)
            content = pyperclip.paste()
            return {"status": "success", "message": "Copied", "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class SystemControl:
    """System control operations"""
    
    def get_system_info(self):
        """Get detailed system info"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery()
            
            info = {
                "cpu": f"{cpu}%",
                "ram_used": f"{memory.percent}%",
                "ram_available": f"{round(memory.available / (1024**3), 1)} GB",
                "ram_total": f"{round(memory.total / (1024**3), 1)} GB",
                "disk_used": f"{disk.percent}%",
                "disk_free": f"{round(disk.free / (1024**3), 1)} GB",
            }
            
            if battery:
                info["battery"] = f"{battery.percent}%"
                info["charging"] = "Yes" if battery.power_plugged else "No"
            
            logger.info("System info retrieved")
            return {"status": "success", "data": info}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def lock(self):
        """Lock computer"""
        try:
            logger.warning("Locking computer...")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return {"status": "success", "message": "Computer locked"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def shutdown(self, delay=0):
        """Shutdown computer"""
        try:
            logger.warning(f"Shutdown in {delay} seconds...")
            os.system(f"shutdown /s /t {delay}")
            return {"status": "success", "message": f"Shutting down in {delay} seconds"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def restart(self, delay=0):
        """Restart computer"""
        try:
            logger.warning(f"Restart in {delay} seconds...")
            os.system(f"shutdown /r /t {delay}")
            return {"status": "success", "message": f"Restarting in {delay} seconds"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def sleep(self):
        """Put computer to sleep"""
        try:
            logger.info("Putting computer to sleep...")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return {"status": "success", "message": "Computer sleeping"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def cancel_shutdown(self):
        """Cancel scheduled shutdown"""
        try:
            os.system("shutdown /a")
            logger.info("Shutdown cancelled")
            return {"status": "success", "message": "Shutdown cancelled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global instances
_apps = AppManager()
_screenshot = ScreenshotManager()
_volume = VolumeControl()
_brightness = BrightnessControl()
_clipboard = ClipboardManager()
_system = SystemControl()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

# App Management
def open_app(app_name=None, name=None, **kwargs):
    """Open app via Start Menu"""
    final_name = app_name or name
    return _apps.open_app(final_name)

def close_app(app_name=None, name=None, **kwargs):
    """Close app"""
    final_name = app_name or name
    return _apps.close_app(final_name)

def minimize_all(**kwargs):
    """Minimize all windows"""
    return _apps.minimize_all()

def switch_window(**kwargs):
    """Switch window"""
    return _apps.switch_window()

# Screenshot
def screenshot(filename=None, **kwargs):
    """Take full screenshot"""
    return _screenshot.take_full(filename)

def screenshot_region(x, y, width, height, filename=None, **kwargs):
    """Take region screenshot"""
    return _screenshot.take_region(x, y, width, height, filename)

def screenshot_window(filename=None, **kwargs):
    """Take active window screenshot"""
    return _screenshot.take_window(filename)

# Volume
def volume_up(steps=5, **kwargs):
    return _volume.volume_up(steps)

def volume_down(steps=5, **kwargs):
    return _volume.volume_down(steps)

def mute(**kwargs):
    return _volume.mute()

# Brightness
def brightness_up(steps=10, **kwargs):
    return _brightness.brightness_up(steps)

def brightness_down(steps=10, **kwargs):
    return _brightness.brightness_down(steps)

# Clipboard
def copy(text, **kwargs):
    return _clipboard.copy(text)

def paste(**kwargs):
    return _clipboard.paste()

def copy_action(**kwargs):
    return _clipboard.copy_action()

def paste_action(**kwargs):
    return _clipboard.paste_action()

# System
def system_info(**kwargs):
    return _system.get_system_info()

def lock(**kwargs):
    return _system.lock()

def shutdown(delay=0, **kwargs):
    return _system.shutdown(delay)

def restart(delay=0, **kwargs):
    return _system.restart(delay)

def sleep(**kwargs):
    return _system.sleep()

def cancel_shutdown(**kwargs):
    return _system.cancel_shutdown()

# ============================================================
# MACRO TOOLS
# ============================================================

def control_volume(action: str = None, steps: int = 5, **kwargs):
    """Macro tool for volume"""
    if action is None:
        return {"status": "error", "message": "No action specified"}
    action = action.lower()
    if action == "up" or action == "increase":
        return _volume.volume_up(steps)
    elif action == "down" or action == "decrease":
        return _volume.volume_down(steps)
    elif action == "mute" or action == "unmute" or action == "toggle":
        return _volume.mute()
    return {"status": "error", "message": f"Unknown volume action: {action}"}

def control_brightness(action: str = None, steps: int = 10, **kwargs):
    """Macro tool for brightness"""
    if action is None:
        return {"status": "error", "message": "No action specified"}
    action = action.lower()
    if action == "up" or action == "increase":
        return _brightness.brightness_up(steps)
    elif action == "down" or action == "decrease":
        return _brightness.brightness_down(steps)
    return {"status": "error", "message": f"Unknown brightness action: {action}"}

def control_system(action: str = None, delay: int = 0, **kwargs):
    """Macro tool for system power"""
    if action is None:
        return {"status": "error", "message": "No action specified"}
    action = action.lower()
    if action == "lock":
        return _system.lock()
    elif action == "shutdown":
        return _system.shutdown(delay)
    elif action == "restart":
        return _system.restart(delay)
    elif action == "sleep":
        return _system.sleep()
    elif action == "cancel_shutdown" or action == "cancel":
        return _system.cancel_shutdown()
    elif action == "info" or action == "status":
        return _system.get_system_info()
    return {"status": "error", "message": f"Unknown system action: {action}"}


def launch_screen_recorder(app_name=None, **kwargs):
    """
    Scan the system for screen recording applications (like OBS Studio, ShareX, Bandicam,
    Windows Snipping Tool, Xbox Game Bar) and launch it.
    If no apps are found, return an error message.
    """
    import os
    import sys
    import subprocess
    import time
    
    # Only supports Windows since we are in a Windows workspace environment
    if sys.platform != "win32":
        return {"status": "error", "message": "Screen recording launch is only supported on Windows systems."}
        
    recorders = []
    
    # 1. Check system Start Menu path for shortcuts
    start_menu_paths = [
        os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs")
    ]
    
    keywords = ["obs", "sharex", "bandicam", "screentogif", "camtasia", "snagit", "captura", "recorder", "recording"]
    
    for base_path in start_menu_paths:
        if not os.path.exists(base_path):
            continue
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".lnk"):
                    name_lower = file.lower()
                    if any(kw in name_lower for kw in keywords) and "uninstall" not in name_lower:
                        app_name_found = file[:-4] # strip .lnk
                        shortcut_path = os.path.join(root, file)
                        recorders.append({
                            "name": app_name_found,
                            "type": "shortcut",
                            "path": shortcut_path
                        })

    # 2. Check common paths directly
    common_exes = {
        "OBS Studio": [
            "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
            "C:\\Program Files (x86)\\obs-studio\\bin\\64bit\\obs64.exe"
        ],
        "ShareX": [
            "C:\\Program Files\\ShareX\\ShareX.exe",
            "C:\\Program Files (x86)\\ShareX\\ShareX.exe",
            os.path.expandvars("%LocalAppData%\\ShareX\\ShareX.exe")
        ],
        "Bandicam": [
            "C:\\Program Files\\Bandicam\\bdcam.exe",
            "C:\\Program Files (x86)\\Bandicam\\bdcam.exe"
        ],
        "ScreenToGif": [
            "C:\\Program Files\\ScreenToGif\\ScreenToGif.exe",
            os.path.expandvars("%LocalAppData%\\ScreenToGif\\ScreenToGif.exe")
        ]
    }
    
    for name, paths in common_exes.items():
        # Avoid duplicate entries
        if any(name.lower() in r["name"].lower() for r in recorders):
            continue
        for path in paths:
            if os.path.exists(path):
                recorders.append({
                    "name": name,
                    "type": "executable",
                    "path": path
                })
                break

    # Add Windows native options as fallback
    native_options = [
        {
            "name": "Windows Snipping Tool (Native)",
            "type": "native_cmd",
            "command": "snippingtool"
        },
        {
            "name": "Xbox Game Bar (Native)",
            "type": "shortcut_trigger",
            "keys": ["win", "alt", "r"]
        }
    ]
    
    # 3. If user requested a specific app_name, try to match it first
    if app_name:
        req_lower = app_name.lower().strip()
        matched = None
        for r in recorders:
            if req_lower in r["name"].lower():
                matched = r
                break
        
        if not matched:
            for opt in native_options:
                if req_lower in opt["name"].lower() or ("snipping" in req_lower and "snipping" in opt["name"].lower()) or ("xbox" in req_lower and "xbox" in opt["name"].lower()):
                    matched = opt
                    break
                    
        if matched:
            return _launch_recorder_item(matched)
        else:
            return {
                "status": "error",
                "message": f"Could not find a screen recorder matching '{app_name}' on your system."
            }

    # 4. If no specific app requested, choose the best one
    third_party = [r for r in recorders if r["type"] in ("shortcut", "executable")]
    if third_party:
        best_choice = third_party[0]
        return _launch_recorder_item(best_choice)
        
    logger.info("No third-party screen recording apps found. Falling back to Snipping Tool.")
    return _launch_recorder_item(native_options[0])


def _launch_recorder_item(item):
    import os
    import subprocess
    import pyautogui
    try:
        name = item["name"]
        logger.info(f"Attempting to launch recorder: {name}")
        
        if item["type"] == "shortcut" or item["type"] == "executable":
            os.startfile(item["path"])
            return {"status": "success", "message": f"Successfully launched screen recording app: {name}"}
            
        elif item["type"] == "native_cmd":
            subprocess.Popen([item["command"]], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0)
            return {
                "status": "success", 
                "message": f"No third-party recorder found. Launched native Windows Snipping Tool for screen recording."
            }
            
        elif item["type"] == "shortcut_trigger":
            pyautogui.hotkey(*item["keys"])
            return {
                "status": "success", 
                "message": f"Triggered native Xbox Game Bar screen recording shortcut ({'+'.join(item['keys'])})."
            }
            
    except Exception as e:
        logger.error(f"Error launching recorder {item.get('name')}: {e}")
        return {"status": "error", "message": f"Failed to launch {item.get('name')}: {str(e)}"}
        
    return {"status": "error", "message": "Unknown recorder item configuration."}