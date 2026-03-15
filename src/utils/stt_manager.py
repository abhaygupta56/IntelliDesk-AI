"""
STT Manager - Gemini-style continuous listening
With self-voice blocking and noise reduction
"""

import speech_recognition as sr
import threading
import time
from src.utils.logger import Logger

logger = Logger.get_logger("STT")


# Lazy import to avoid circular dependency
def _is_system_speaking():
    """Check if TTS is active"""
    try:
        from src.utils.voice_manager import is_speaking
        return is_speaking()
    except:
        return False


class STTManager:
    """Speech-to-Text with noise handling"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.is_enabled = True
        self._stop_requested = False
        
        # Gemini-style settings
        self.recognizer.pause_threshold = 0.8 # Stop after 1.5s silence
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.energy_threshold = 300  # Default, will calibrate
        self.recognizer.dynamic_energy_threshold = True
        
        logger.info("STT Manager initialized")
    
    def _get_microphone(self):
        """Get or create microphone instance"""
        if self.microphone is None:
            self.microphone = sr.Microphone()
        return self.microphone
    
    def calibrate_noise(self):
        """Calibrate for ambient noise"""
        try:
            with self._get_microphone() as source:
                logger.info("🎤 Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info(f"✅ Noise threshold: {self.recognizer.energy_threshold:.0f}")
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
    
    def listen_once(self, timeout=5):
        """
        Listen for single command
        Returns: text or None
        """
        if not self.is_enabled:
            return None
        
        # Wait if system is speaking
        wait_count = 0
        while _is_system_speaking():
            if wait_count == 0:
                logger.info("⏸️ Waiting for TTS to finish...")
            time.sleep(0.3)
            wait_count += 1
            if wait_count > 30:  # Max 9 seconds wait
                logger.warning("⚠️ TTS timeout, proceeding...")
                break
        
        # Small gap after TTS
        if wait_count > 0:
            time.sleep(0.5)
        
        if self._stop_requested:
            return None
        
        self.is_listening = True
        
        try:
            with self._get_microphone() as source:
                logger.info("🎤 Listening... (speak now)")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=8 # Max 15 sec per phrase
                )
                
                logger.info("🔄 Processing speech...")
                
                text = self.recognizer.recognize_google(
                    audio,
                    language="en-IN"
                )
                
                text = text.strip()
                
                if text:
                    logger.info(f"✅ Recognized: {text}")
                    return text
                else:
                    return None
        
        except sr.WaitTimeoutError:
            # Silent - no speech detected (normal)
            return None
        
        except sr.UnknownValueError:
            # Could not understand (normal)
            return None
        
        except sr.RequestError as e:
            logger.error(f"❌ API error: {e}")
            return None
        
        except Exception as e:
            logger.error(f"❌ STT error: {e}")
            return None
        
        finally:
            self.is_listening = False
    
    def listen_async(self, callback, timeout=5):
        """
        Listen in background thread
        callback(text) called with recognized text
        """
        def listen_thread():
            text = self.listen_once(timeout=timeout)
            if text and callback:
                callback(text)
        
        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop listening"""
        self._stop_requested = True
        self.is_listening = False
        logger.info("🛑 STT stopped")
    
    def reset(self):
        """Reset stop flag"""
        self._stop_requested = False
    
    def toggle(self):
        """Toggle STT on/off"""
        self.is_enabled = not self.is_enabled
        status = "enabled" if self.is_enabled else "disabled"
        logger.info(f"STT {status}")
        return self.is_enabled
    
    def is_active(self):
        """Check if currently listening"""
        return self.is_listening


# Global instance
stt_manager = STTManager()


# Convenience functions
def listen(timeout=5):
    """Listen for command"""
    return stt_manager.listen_once(timeout)

def listen_async(callback, timeout=5):
    """Listen in background"""
    stt_manager.listen_async(callback, timeout)

def stop_listening():
    """Stop listening"""
    stt_manager.stop()

def reset_stt():
    """Reset STT"""
    stt_manager.reset()

def toggle_stt():
    """Toggle STT"""
    return stt_manager.toggle()

def is_listening():
    """Check if listening"""
    return stt_manager.is_active()

def calibrate():
    """Calibrate noise"""
    stt_manager.calibrate_noise()