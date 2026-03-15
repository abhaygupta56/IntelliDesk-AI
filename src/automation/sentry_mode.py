"""
Sentry Mode - Ultra-Light Motion Detection
Auto-breaks | Telegram alerts | Self-destruct photos
"""

import cv2
import numpy as np
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from src.utils.telegram_notifier import send_alert, is_configured
from src.utils.logger import Logger

logger = Logger.get_logger("Sentry")


class SentryMode:
    """Ultra-light surveillance with auto-breaks"""
    
    def __init__(self):
        self.is_active = False
        self.thread = None
        self.camera = None
        self.temp_dir = Path("temp_sentry")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.config = {
            "max_duration_min": 120,
            "check_interval_sec": 5,
            "motion_threshold": 10,
            "rest_after_min": 20,
            "rest_duration_min": 5,
            "max_alerts": 5,
        }
        
        self.stats = {
            "started_at": None,
            "alerts_sent": 0,
            "last_motion": None,
        }
    
    def start(self, duration_min=None):
        """Start sentry mode"""
        if self.is_active:
            return {"status": "error", "message": "Sentry already running"}
        
        if not is_configured():
            return {
                "status": "error",
                "message": "Telegram not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env"
            }
        
        if duration_min:
            self.config["max_duration_min"] = min(duration_min, 120)
        
        self.is_active = True
        self.stats["started_at"] = datetime.now()
        self.stats["alerts_sent"] = 0
        
        self.thread = threading.Thread(target=self._surveillance_loop, daemon=True)
        self.thread.start()
        
        duration = self.config["max_duration_min"]
        logger.info(f"Sentry mode activated for {duration} min")
        
        return {
            "status": "success",
            "message": f"🛡️ Sentry mode activated for {duration} minutes",
            "data": {"duration": duration}
        }
    
    def stop(self):
        """Stop sentry mode"""
        if not self.is_active:
            return {"status": "error", "message": "Sentry not running"}
        
        self.is_active = False
        self._release_camera()
        
        alerts = self.stats["alerts_sent"]
        logger.info(f"Sentry stopped. {alerts} alerts sent")
        
        return {
            "status": "success",
            "message": f"🛡️ Sentry stopped. {alerts} alerts sent",
            "data": self.stats.copy()
        }
    
    def status(self):
        """Get current status"""
        if not self.is_active:
            return {
                "status": "success",
                "message": "Sentry mode inactive",
                "data": {"active": False}
            }
        
        elapsed = (datetime.now() - self.stats["started_at"]).seconds // 60
        remaining = self.config["max_duration_min"] - elapsed
        
        return {
            "status": "success",
            "message": f"🛡️ Sentry active | {remaining} min left | {self.stats['alerts_sent']} alerts",
            "data": {
                "active": True,
                "elapsed_min": elapsed,
                "remaining_min": remaining,
                "alerts": self.stats["alerts_sent"]
            }
        }
    
    def _surveillance_loop(self):
        """Main surveillance loop with auto-breaks"""
        logger.info("Surveillance started")
        
        previous_frame = None
        work_start = datetime.now()
        
        while self.is_active:
            try:
                elapsed_min = (datetime.now() - self.stats["started_at"]).seconds // 60
                
                if elapsed_min >= self.config["max_duration_min"]:
                    logger.info("Max duration reached")
                    self.is_active = False
                    break
                
                if self.stats["alerts_sent"] >= self.config["max_alerts"]:
                    logger.info("Max alerts reached")
                    self.is_active = False
                    break
                
                work_elapsed = (datetime.now() - work_start).seconds // 60
                if work_elapsed >= self.config["rest_after_min"]:
                    self._take_break()
                    work_start = datetime.now()
                    previous_frame = None
                    continue
                
                frame = self._capture_frame()
                
                if frame is None:
                    time.sleep(2)
                    continue
                
                if previous_frame is not None:
                    motion = self._detect_motion(previous_frame, frame)
                    
                    if motion:
                        logger.warning("Motion detected!")
                        self._handle_motion(frame)
                
                previous_frame = frame
                time.sleep(self.config["check_interval_sec"])
            
            except Exception as e:
                logger.error(f"Surveillance error: {e}")
                time.sleep(5)
        
        self._release_camera()
        logger.info("Surveillance ended")
    
    def _capture_frame(self):
        """Capture single frame"""
        try:
            if self.camera is None:
                self.camera = cv2.VideoCapture(1)
                time.sleep(1)
            
            ret, frame = self.camera.read()
            
            if not ret:
                self._release_camera()
                return None
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            return gray
        
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            self._release_camera()
            return None
    
    def _detect_motion(self, prev, curr):
        """Compare frames for motion"""
        try:
            diff = cv2.absdiff(prev, curr)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            
            motion_pixels = np.sum(thresh == 255)
            total_pixels = thresh.size
            motion_percent = (motion_pixels / total_pixels) * 100
            
            return motion_percent > self.config["motion_threshold"]
        
        except Exception as e:
            logger.error(f"Motion detection error: {e}")
            return False
    
    def _handle_motion(self, frame):
        """Handle detected motion"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_path = self.temp_dir / f"alert_{timestamp}.jpg"
            
            if self.camera:
                ret, color_frame = self.camera.read()
                if ret:
                    cv2.imwrite(str(photo_path), color_frame)
            
            message = f"⚠️ Motion detected!\n🎯 Alert #{self.stats['alerts_sent'] + 1}"
            
            success = send_alert(message, str(photo_path))
            
            if success:
                self.stats["alerts_sent"] += 1
                self.stats["last_motion"] = datetime.now()
                logger.info(f"Alert sent ({self.stats['alerts_sent']})")
            
            try:
                photo_path.unlink()
            except:
                pass
        
        except Exception as e:
            logger.error(f"Alert handling error: {e}")
    
    def _take_break(self):
        """Auto-break to prevent overheating"""
        logger.info(f"Taking {self.config['rest_duration_min']} min break...")
        self._release_camera()
        time.sleep(self.config["rest_duration_min"] * 60)
        logger.info("Break over, resuming surveillance")
    
    def _release_camera(self):
        """Release camera resource"""
        if self.camera:
            self.camera.release()
            self.camera = None


sentry = SentryMode()


def start_sentry(duration_min=None, **kwargs):
    """Start sentry mode"""
    return sentry.start(duration_min)


def stop_sentry(**kwargs):
    """Stop sentry mode"""
    return sentry.stop()


def sentry_status(**kwargs):
    """Get sentry status"""
    return sentry.status()