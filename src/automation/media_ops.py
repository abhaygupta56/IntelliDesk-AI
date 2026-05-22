"""
Media Operations Module
Features:
- Play/Pause media
- Next/Previous track
- Media controls
- Screen recording (basic)
"""

import pyautogui
import time
from src.utils.logger import Logger

logger = Logger.get_logger("Media")


class MediaControl:
    """Media playback controls"""
    
    def play_pause(self):
        """Play/Pause media"""
        try:
            pyautogui.press('playpause')
            logger.info("Media: Play/Pause")
            return {"status": "success", "message": "Play/Pause toggled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def next_track(self):
        """Next track"""
        try:
            pyautogui.press('nexttrack')
            logger.info("Media: Next track")
            return {"status": "success", "message": "Next track"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def previous_track(self):
        """Previous track"""
        try:
            pyautogui.press('prevtrack')
            logger.info("Media: Previous track")
            return {"status": "success", "message": "Previous track"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def stop(self):
        """Stop media"""
        try:
            pyautogui.press('stop')
            logger.info("Media: Stop")
            return {"status": "success", "message": "Media stopped"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global instance
_media = MediaControl()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def play_pause(**kwargs):
    return _media.play_pause()

def next_track(**kwargs):
    return _media.next_track()

def previous_track(**kwargs):
    return _media.previous_track()

def stop(**kwargs):
    return _media.stop()

def control_media(action: str = None, **kwargs):
    """Macro tool to control media playback"""
    if action is None:
        return {"status": "error", "message": "No action specified"}
    action = action.lower()
    if action in ["play", "pause", "play_pause", "toggle"]:
        return _media.play_pause()
    elif action in ["next", "forward", "skip"]:
        return _media.next_track()
    elif action in ["previous", "prev", "back"]:
        return _media.previous_track()
    elif action == "stop":
        return _media.stop()
    else:
        return {"status": "error", "message": f"Unknown media action: {action}"}