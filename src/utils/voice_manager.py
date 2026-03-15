"""
Voice Manager - Gemini-style continuous speech
Features:
- Sentence-by-sentence speech for natural flow
- Stop on command (F10)
- New command interrupts old speech
- 500 char limit (expandable)
"""

import asyncio
import threading
import re
from pathlib import Path
import time
from src.utils.logger import Logger

logger = Logger.get_logger("Voice")


class VoiceManager:
    """Edge TTS with Gemini-style continuous speech"""
    
    DEFAULT_VOICE = "en-IN-NeerjaNeural"
    MAX_CHARS = 500  # Expandable to 1000 after testing
    
    VOICES = {
        "female_indian": "en-IN-NeerjaNeural",
        "male_indian": "en-IN-PrabhatNeural",
        "female_hindi": "hi-IN-SwaraNeural",
        "female_us": "en-US-JennyNeural",
    }
    
    def __init__(self):
        self.enabled = True
        self.current_voice = self.DEFAULT_VOICE
        self.temp_dir = Path("data/voice_cache")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Voice settings
        self.rate = "+5%"
        self.pitch = "+2Hz"
        self.volume = "+0%"
        
        # Initialize pygame
        self._init_pygame()
        
        # Queue and threading
        self.speech_queue = []
        self.queue_lock = threading.Lock()
        self._processing = False
        self._stop_requested = False
        self._currently_speaking = False
        
        logger.info(f"Voice manager initialized (max {self.MAX_CHARS} chars)")
    
    def _init_pygame(self):
        """Initialize pygame mixer"""
        try:
            import pygame
            pygame.mixer.init()
            logger.info("Audio engine ready")
        except Exception as e:
            logger.error(f"Audio init failed: {e}")
    
    def _split_into_sentences(self, text: str) -> list:
        """
        Split text into sentences for natural speech flow
        Handles: . ! ? and also Hindi sentence endings
        """
        if not text:
            return []
        
        text = text.strip()
        
        # Split by sentence endings
        pattern = r'(?<=[.!?।|])\s+'
        sentences = re.split(pattern, text)
        
        # Clean and filter
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 2:
                result.append(sentence)
        
        if not result:
            result = [text]
        
        logger.info(f"Split into {len(result)} sentences")
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean text for TTS"""
        if not text:
            return ""
        
        # Remove emojis and special chars
        clean = text.replace("✅", "").replace("❌", "").replace("⚠️", "")
        clean = clean.replace("→", "").replace("...", ".").replace("•", "")
        clean = clean.replace("💡", "").replace("📁", "").replace("🔊", "")
        clean = clean.replace("🔇", "").replace("✦", "").replace("⟳", "")
        clean = clean.replace("```", "").replace("`", "")
        clean = clean.replace("  ", " ").strip()
        
        # Apply character limit with smart truncation
        if len(clean) > self.MAX_CHARS:
            truncated = clean[:self.MAX_CHARS]
            last_period = truncated.rfind('.')
            last_question = truncated.rfind('?')
            last_exclaim = truncated.rfind('!')
            
            cut_point = max(last_period, last_question, last_exclaim)
            
            if cut_point > self.MAX_CHARS // 2:
                clean = truncated[:cut_point + 1]
            else:
                clean = truncated + "..."
            
            logger.info(f"Text truncated to {len(clean)} chars")
        
        return clean
    
    def speak(self, text: str, force: bool = False):
        """
        Queue speech - Gemini style (sentence by sentence)
        """
        if not self.enabled and not force:
            return
        
        if not text or not text.strip():
            return
        
        # Clean text
        clean_text = self._clean_text(text)
        if not clean_text:
            return
        
        # Split into sentences
        sentences = self._split_into_sentences(clean_text)
        
        # Add all sentences to queue
        with self.queue_lock:
            for sentence in sentences:
                self.speech_queue.append(sentence)
            logger.info(f"Queued {len(sentences)} sentences (Total: {len(self.speech_queue)})")
        
        # Start processing if not already running
        if not self._processing:
            self._stop_requested = False
            thread = threading.Thread(target=self._process_queue, daemon=True)
            thread.start()
    
    def interrupt_and_speak(self, text: str):
        """
        Stop current speech and speak new text immediately
        Used when user gives new command
        """
        logger.info("Interrupting current speech...")
        self.stop()
        time.sleep(0.1)
        self.speak(text, force=True)
    
    def stop(self):
        """
        Stop current speech and clear queue
        Called on F10 or new command
        """
        logger.info("Stop requested")
        
        self._stop_requested = True
        
        # Clear queue
        with self.queue_lock:
            count = len(self.speech_queue)
            self.speech_queue.clear()
        
        # Stop pygame playback
        try:
            import pygame
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except:
            pass
        
        self._currently_speaking = False
        logger.info(f"Stopped. Cleared {count} items")
    
    def _process_queue(self):
        """Process all sentences in queue sequentially"""
        self._processing = True
        self._stop_requested = False
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while True:
                # Check stop flag
                if self._stop_requested:
                    logger.info("Stop flag detected")
                    break
                
                # Get next sentence
                with self.queue_lock:
                    if not self.speech_queue:
                        break
                    sentence = self.speech_queue.pop(0)
                
                if self._stop_requested:
                    break
                
                # Speak sentence
                logger.info(f"Speaking: {sentence[:40]}...")
                self._currently_speaking = True
                loop.run_until_complete(self._speak_async(sentence))
                self._currently_speaking = False
                
                # Natural pause between sentences
                if not self._stop_requested:
                    time.sleep(0.15)
        
        except Exception as e:
            logger.error(f"Queue error: {e}")
        
        finally:
            loop.close()
            self._processing = False
            self._currently_speaking = False
            logger.info("Queue processor stopped")
    
    async def _speak_async(self, text: str):
        """Generate and play single sentence"""
        if self._stop_requested:
            return
        
        try:
            import edge_tts
            import pygame
            
            if not text or len(text) < 2:
                return
            
            # Generate temp file
            temp_file = self.temp_dir / f"voice_{int(time.time()*1000)}.mp3"
            
            # Generate speech
            communicate = edge_tts.Communicate(
                text,
                self.current_voice,
                rate=self.rate,
                pitch=self.pitch,
                volume=self.volume
            )
            await communicate.save(str(temp_file))
            
            # Check stop before playing
            if self._stop_requested:
                try:
                    temp_file.unlink()
                except:
                    pass
                return
            
            # Play audio
            try:
                pygame.mixer.music.load(str(temp_file))
                pygame.mixer.music.play()
                
                # Wait with stop check every 50ms
                while pygame.mixer.music.get_busy():
                    if self._stop_requested:
                        pygame.mixer.music.stop()
                        break
                    await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Playback error: {e}")
            
            # Cleanup
            try:
                pygame.mixer.music.unload()
                await asyncio.sleep(0.1)
                temp_file.unlink()
            except:
                pass
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def speak_instant(self, text: str):
        """Speak instantly (short confirmations)"""
        thread = threading.Thread(
            target=self._speak_instant_sync,
            args=(text,),
            daemon=True
        )
        thread.start()
    
    def _speak_instant_sync(self, text: str):
        """Instant speech thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._speak_async(text))
        finally:
            loop.close()
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self._currently_speaking or self._processing
    
    def get_queue_size(self) -> int:
        """Get pending sentences count"""
        with self.queue_lock:
            return len(self.speech_queue)
    
    def set_natural_preset(self, preset: str = "balanced"):
        """Apply voice preset"""
        presets = {
            "balanced": {"rate": "+5%", "pitch": "+2Hz", "volume": "+0%"},
            "energetic": {"rate": "+15%", "pitch": "+8Hz", "volume": "+5%"},
            "calm": {"rate": "-5%", "pitch": "-3Hz", "volume": "-5%"},
            "professional": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
        }
        
        if preset in presets:
            self.rate = presets[preset]["rate"]
            self.pitch = presets[preset]["pitch"]
            self.volume = presets[preset]["volume"]
            logger.info(f"Voice preset: {preset}")
    
    def toggle(self) -> bool:
        """Toggle voice on/off"""
        self.enabled = not self.enabled
        status = "enabled" if self.enabled else "disabled"
        logger.info(f"Voice {status}")
        
        if self.enabled:
            self.speak_instant("Voice enabled")
        
        return self.enabled
    
    def is_enabled(self) -> bool:
        """Check if voice is enabled"""
        return self.enabled
    
    def set_voice(self, voice_key: str):
        """Change voice"""
        if voice_key in self.VOICES:
            self.current_voice = self.VOICES[voice_key]
            self.speak_instant("Voice changed")
    
    def clear_queue(self):
        """Clear pending speech without stopping current"""
        with self.queue_lock:
            count = len(self.speech_queue)
            self.speech_queue.clear()
            logger.info(f"Cleared {count} pending items")
    
    def cleanup(self):
        """Full cleanup on app exit"""
        logger.info("Voice cleanup...")
        self.stop()
        
        try:
            import pygame
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
        
        try:
            for file in self.temp_dir.glob("voice_*.mp3"):
                try:
                    file.unlink()
                except:
                    pass
        except:
            pass
        
        logger.info("Voice cleanup complete")


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════
voice_manager = VoiceManager()


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def speak(text: str, force: bool = False):
    voice_manager.speak(text, force)

def speak_instant(text: str):
    voice_manager.speak_instant(text)

def interrupt_and_speak(text: str):
    voice_manager.interrupt_and_speak(text)

def stop_voice():
    voice_manager.stop()

def toggle_voice() -> bool:
    return voice_manager.toggle()

def is_voice_enabled() -> bool:
    return voice_manager.is_enabled()

def is_speaking() -> bool:
    return voice_manager.is_speaking()

def set_voice_preset(preset: str):
    voice_manager.set_natural_preset(preset)

def cleanup_voice():
    voice_manager.cleanup()