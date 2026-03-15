"""
IntelliDesk AI - Spotlight App v5
Premium Glassmorphic Command Palette
Clean corners, no halo artifacts
"""

import customtkinter as ctk
import sys
import os
import threading
import ctypes
from typing import Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum
import queue
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════
from src.core.conversation_manager import conversation_manager
from src.utils.voice_manager import toggle_voice, is_voice_enabled, speak, stop_voice, is_speaking
from src.utils.stt_manager import listen_async, is_listening, listen, stop_listening, reset_stt

# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

# ═══════════════════════════════════════════════════════════════════════════════
# OPTIONAL IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════
keyboard = None
if IS_WINDOWS:
    try:
        import keyboard
    except ImportError:
        print("⚠ 'keyboard' module not found. Global hotkeys disabled.")

HAS_TRAY = False
pystray = None
Image = None
ImageDraw = None

try:
    import pystray
    from pystray import MenuItem as TrayMenuItem
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    print("⚠ 'pystray' or 'PIL' not found. System tray disabled.")

HAS_BLUR = False
if IS_WINDOWS:
    try:
        from BlurWindow.blurWindow import blur as apply_blur
        HAS_BLUR = True
    except ImportError:
        print("⚠ 'BlurWindow' not found. Acrylic blur disabled.")

ctk.set_appearance_mode("dark")


# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM GLASSMORPHIC THEME
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Theme:
    """Premium glass theme"""
    
    # Glass layers
    glass_primary: str = "#1c1c1e"
    glass_elevated: str = "#252528"
    glass_surface: str = "#2c2c2f"
    
    # Borders
    border_subtle: str = "#3a3a3c"
    border_inner: str = "#333335"
    
    # Text hierarchy
    text_primary: str = "#ffffff"
    text_secondary: str = "#ababab"
    text_tertiary: str = "#7a7a7c"
    text_placeholder: str = "#5c5c5e"
    
    # Accent colors
    accent: str = "#3b82f6"
    accent_soft: str = "#2563eb"
    success: str = "#34d399"
    warning: str = "#fbbf24"
    error: str = "#f87171"
    info: str = "#60a5fa"


THEME = Theme()


class Status(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    NEEDS_INFO = "needs_info"
    PROCESSING = "processing"


# ═══════════════════════════════════════════════════════════════════════════════
# THREAD-SAFE UI UPDATER
# ═══════════════════════════════════════════════════════════════════════════════
class ThreadSafeUI:
    """Thread-safe UI updates for Tkinter"""
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.queue: queue.Queue[Callable] = queue.Queue()
        self._poll()
    
    def _poll(self):
        try:
            while True:
                callback = self.queue.get_nowait()
                callback()
        except queue.Empty:
            pass
        finally:
            self.root.after(10, self._poll)
    
    def run(self, callback: Callable):
        self.queue.put(callback)
    
    def run_immediate(self, callback: Callable):
        if threading.current_thread() is threading.main_thread():
            callback()
        else:
            self.queue.put(callback)


# ═══════════════════════════════════════════════════════════════════════════════
# SMOOTH ANIMATOR
# ═══════════════════════════════════════════════════════════════════════════════
class Animator:
    """Premium smooth animations"""
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self._active: Dict[str, bool] = {}
    
    def cancel(self, animation_id: str):
        self._active[animation_id] = False
    
    def cancel_all(self):
        for key in self._active:
            self._active[key] = False
    
    def fade_in(self, duration_ms: int = 200, on_complete: Optional[Callable] = None, animation_id: str = "fade"):
        """Smooth fade in with ease-out-cubic"""
        self.cancel(animation_id)
        self._active[animation_id] = True
        
        steps = max(1, duration_ms // 8)
        delay = duration_ms // steps
        
        def animate(step: int):
            if not self._active.get(animation_id, False):
                return
            
            if step <= steps:
                t = step / steps
                alpha = 1 - pow(1 - t, 3)
                try:
                    self.root.attributes("-alpha", alpha)
                except:
                    pass
                self.root.after(delay, animate, step + 1)
            else:
                self._active[animation_id] = False
                try:
                    self.root.attributes("-alpha", 1.0)
                except:
                    pass
                if on_complete:
                    on_complete()
        
        self.root.attributes("-alpha", 0.0)
        animate(1)
    
    def fade_out(self, duration_ms: int = 160, on_complete: Optional[Callable] = None, animation_id: str = "fade"):
        """Smooth fade out with ease-in-quad"""
        self.cancel(animation_id)
        self._active[animation_id] = True
        
        steps = max(1, duration_ms // 8)
        delay = duration_ms // steps
        
        def animate(step: int):
            if not self._active.get(animation_id, False):
                return
            
            if step <= steps:
                t = step / steps
                alpha = 1 - (t * t)
                try:
                    self.root.attributes("-alpha", alpha)
                except:
                    pass
                self.root.after(delay, animate, step + 1)
            else:
                self._active[animation_id] = False
                if on_complete:
                    on_complete()
        
        animate(1)
    
    def pulse(self, label: ctk.CTkLabel, colors: tuple = (THEME.accent, THEME.text_tertiary), interval_ms: int = 450, animation_id: str = "pulse"):
        """Pulsing color animation"""
        self._active[animation_id] = True
        
        def animate(index: int):
            if not self._active.get(animation_id, False):
                return
            try:
                label.configure(text_color=colors[index % len(colors)])
            except:
                return
            self.root.after(interval_ms, animate, index + 1)
        
        animate(0)


# ═══════════════════════════════════════════════════════════════════════════════
# WINDOWS ACRYLIC BLUR
# ═══════════════════════════════════════════════════════════════════════════════
class WindowsEffects:
    """Windows 10/11 visual effects"""
    
    @staticmethod
    def apply_blur(root: ctk.CTk) -> bool:
        """Apply acrylic blur to window"""
        if not IS_WINDOWS or not HAS_BLUR:
            return False
        
        try:
            root.update_idletasks()
            root.update()
            
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            if hwnd == 0:
                hwnd = root.winfo_id()
            
            if hwnd == 0:
                return False
            
            apply_blur(hwnd, Acrylic=True, Dark=True)
            return True
            
        except Exception as e:
            print(f"⚠ Blur failed: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM TRAY
# ═══════════════════════════════════════════════════════════════════════════════
class SystemTray:
    """System tray icon manager"""
    
    def __init__(self, on_show: Callable, on_quit: Callable, app_name: str = "IntelliDesk AI"):
        self.on_show = on_show
        self.on_quit = on_quit
        self.app_name = app_name
        self.icon: Optional[pystray.Icon] = None
        self._running = False
    
    def _create_icon(self) -> 'Image.Image':
        """Create modern hexagon tray icon"""
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        draw.rounded_rectangle(
            [6, 6, size - 6, size - 6],
            radius=14,
            fill=(59, 130, 246, 255)
        )
        
        import math
        cx, cy = size // 2, size // 2
        r = 15
        points = [(cx + r * math.cos(math.pi / 3 * i - math.pi / 2),
                   cy + r * math.sin(math.pi / 3 * i - math.pi / 2)) for i in range(6)]
        draw.polygon(points, fill=(255, 255, 255, 255))
        
        return img
    
    def start(self):
        if not HAS_TRAY or self._running:
            return
        
        menu = pystray.Menu(
            TrayMenuItem('Show (Ctrl+Space)', lambda: self.on_show(), default=True),
            pystray.Menu.SEPARATOR,
            TrayMenuItem('Quit', lambda: self.on_quit())
        )
        
        self.icon = pystray.Icon("IntelliDesk", self._create_icon(), self.app_name, menu)
        self._running = True
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def stop(self):
        if self.icon and self._running:
            self._running = False
            try:
                self.icon.stop()
            except:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
# HOTKEY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════
class HotkeyManager:
    """Global hotkey manager"""
    
    def __init__(self):
        self._hotkeys: list = []
        self._enabled = False
    
    def register(self, hotkey: str, callback: Callable) -> bool:
        if not keyboard:
            return False
        
        try:
            keyboard.add_hotkey(hotkey, callback, suppress=False)
            self._hotkeys.append(hotkey)
            self._enabled = True
            return True
        except Exception as e:
            print(f"⚠ Hotkey '{hotkey}' failed: {e}")
            return False
    
    def unregister_all(self):
        if not keyboard or not self._enabled:
            return
        try:
            keyboard.unhook_all()
            self._hotkeys.clear()
            self._enabled = False
        except:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# SPOTLIGHT APP - PREMIUM COMMAND PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
class SpotlightApp:
    """
    Premium glassmorphic command palette
    Clean corners, no halo artifacts
    """
    
    # Dimensions
    WIDTH = 720
    HEIGHT_COLLAPSED = 68
    HEIGHT_EXPANDED = 380
    CORNER_RADIUS = 24
    
    # Animation timing
    FADE_IN_MS = 200
    FADE_OUT_MS = 160
    
    def __init__(self):
        # ─────────────────────────────────────────────────────────────────────
        # ROOT WINDOW
        # ─────────────────────────────────────────────────────────────────────
        self.root = ctk.CTk()
        self.root.title("IntelliDesk AI")
        self.root.withdraw()
        
        # ─────────────────────────────────────────────────────────────────────
        # STATE
        # ─────────────────────────────────────────────────────────────────────
        self.is_visible = False
        self.is_expanded = False
        self.is_processing = False
        self._shutting_down = False
        self.voice_enabled = is_voice_enabled()
        self._mic_active = False
        
        # ─────────────────────────────────────────────────────────────────────
        # SYSTEMS
        # ─────────────────────────────────────────────────────────────────────
        self.ui = ThreadSafeUI(self.root)
        self.animator = Animator(self.root)
        self.hotkeys = HotkeyManager()
        self.tray: Optional[SystemTray] = None
        
        # ─────────────────────────────────────────────────────────────────────
        # BUILD
        # ─────────────────────────────────────────────────────────────────────
        self._configure_window()
        self._build_ui()
        self._bind_events()
        self._setup_hotkeys()
        self._setup_tray()
        
        # Apply blur after build
        self.root.after(100, self._apply_effects)
        self.root.after(180, self.show)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WINDOW CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _configure_window(self):
        """Setup transparent borderless window"""
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0)
        self.root.configure(fg_color=THEME.glass_primary)
        
        self._center_window(self.HEIGHT_COLLAPSED)
    
    def _center_window(self, height: int):
        """Center window above screen center"""
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        x = (sw - self.WIDTH) // 2
        y = (sh - height) // 2 - 80
        
        self.root.geometry(f"{self.WIDTH}x{height}+{x}+{y}")
    
    def _apply_effects(self):
        """Apply platform visual effects"""
        if IS_WINDOWS:
            WindowsEffects.apply_blur(self.root)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UI BUILDING - CLEAN GLASS DESIGN
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_ui(self):
        """Build clean glassmorphic UI"""
        
        # ─────────────────────────────────────────────────────────────────────
        # MAIN GLASS CONTAINER - No border, full fill
        # ─────────────────────────────────────────────────────────────────────
        self.glass = ctk.CTkFrame(
            self.root,
            fg_color=THEME.glass_primary,
            corner_radius=self.CORNER_RADIUS,
            border_width=0
        )
        self.glass.pack(fill="both", expand=True)
        
        # ─────────────────────────────────────────────────────────────────────
        # INPUT ROW
        # ─────────────────────────────────────────────────────────────────────
        self.input_row = ctk.CTkFrame(
            self.glass,
            fg_color="transparent",
            height=54
        )
        self.input_row.pack(fill="x", padx=14, pady=(10, 8))
        self.input_row.pack_propagate(False)
        
        # Logo (Hexagon)
        self.logo = ctk.CTkLabel(
            self.input_row,
            text="⬡",
            font=ctk.CTkFont(family="Segoe UI Symbol", size=28, weight="bold"),
            text_color=THEME.accent,
            width=36
        )
        self.logo.pack(side="left", padx=(6, 10))
        
        # Voice indicator
        self.voice_icon = ctk.CTkLabel(
            self.input_row,
            text="🔈",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=14),
            text_color=THEME.text_tertiary,
            width=22
        )
        self.voice_icon.pack(side="left", padx=(0, 4))
        self._update_voice_indicator()
        
        # Mic indicator
        self.mic_icon = ctk.CTkLabel(
            self.input_row,
            text="🎙",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=14),
            text_color=THEME.text_tertiary,
            width=22
        )
        self.mic_icon.pack(side="left", padx=(0, 10))
        
        # Input field
        self.input_field = ctk.CTkEntry(
            self.input_row,
            placeholder_text="What would you like to do?",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            fg_color=THEME.glass_elevated,
            border_width=1,
            border_color=THEME.border_inner,
            corner_radius=10,
            text_color=THEME.text_primary,
            placeholder_text_color=THEME.text_placeholder,
            height=40
        )
        self.input_field.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Keyboard hints
        self.hints = ctk.CTkFrame(self.input_row, fg_color="transparent")
        self.hints.pack(side="right", padx=(0, 4))
        
        for key in ["↵", "F11", "F12", "Esc"]:
            self._create_hint(self.hints, key).pack(side="left", padx=2)
        
        # ─────────────────────────────────────────────────────────────────────
        # RESULTS PANEL (Hidden initially)
        # ─────────────────────────────────────────────────────────────────────
        self.results = ctk.CTkFrame(self.glass, fg_color="transparent")
        
        # Separator
        self.separator = ctk.CTkFrame(
            self.results,
            fg_color=THEME.border_inner,
            height=1
        )
        self.separator.pack(fill="x", padx=18, pady=(0, 8))
        
        # Output log
        self.output = ctk.CTkTextbox(
            self.results,
            fg_color=THEME.glass_elevated,
            text_color=THEME.text_secondary,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=12,
            border_width=1,
            border_color=THEME.border_inner,
            wrap="word",
            state="disabled",
            height=240
        )
        self.output.pack(fill="both", expand=True, padx=14, pady=(0, 12))
    
    def _create_hint(self, parent, key: str) -> ctk.CTkFrame:
        """Create minimal keyboard hint"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        badge = ctk.CTkLabel(
            frame,
            text=key,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            fg_color=THEME.glass_surface,
            corner_radius=4,
            text_color=THEME.text_tertiary,
            width=22 if len(key) <= 2 else 28,
            height=16
        )
        badge.pack(side="left")
        
        return frame
    
    def _update_voice_indicator(self):
        """Update voice icon"""
        if is_voice_enabled():
            self.voice_icon.configure(text="🔊", text_color=THEME.success)
        else:
            self.voice_icon.configure(text="🔈", text_color=THEME.text_tertiary)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EVENT BINDING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _bind_events(self):
        """Bind keyboard and focus events"""
        self.input_field.bind("<Return>", self._on_submit)
        self.input_field.bind("<Escape>", lambda e: self.hide())
        self.root.bind("<Escape>", lambda e: self.hide())
        self.root.bind("<FocusOut>", self._on_focus_out)
        self.glass.bind("<Button-1>", lambda e: self.input_field.focus_set())
    
    def _on_focus_out(self, event):
        self.root.after(60, self._check_focus)
    
    def _check_focus(self):
        if self._shutting_down or not self.is_visible:
            return
        try:
            if self.root.focus_get() is None:
                self.hide()
        except:
            pass
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SHOW / HIDE / TOGGLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def show(self):
        """Show with smooth fade-in"""
        if self.is_visible:
            self.input_field.focus_set()
            return
        
        self.is_visible = True
        self.animator.cancel_all()
        
        self._collapse()
        self.input_field.delete(0, "end")
        self._update_voice_indicator()
        
        self._center_window(self.HEIGHT_COLLAPSED)
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.input_field.focus_set()
        
        self.animator.fade_in(self.FADE_IN_MS)
    
    def hide(self):
        """Hide with smooth fade-out"""
        if not self.is_visible or self._shutting_down:
            return
        
        self.is_visible = False
        self.animator.cancel_all()
        
        def on_complete():
            self.root.withdraw()
            self._collapse()
            self.input_field.delete(0, "end")
        
        self.animator.fade_out(self.FADE_OUT_MS, on_complete=on_complete)
    
    def toggle(self):
        self.ui.run_immediate(self._toggle_internal)
    
    def _toggle_internal(self):
        self.hide() if self.is_visible else self.show()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPAND / COLLAPSE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _expand(self):
        """Expand to show results"""
        if self.is_expanded:
            return
        self.is_expanded = True
        self.results.pack(fill="both", expand=True)
        self._center_window(self.HEIGHT_EXPANDED)
    
    def _collapse(self):
        """Collapse to input only"""
        if not self.is_expanded:
            return
        self.is_expanded = False
        self.results.pack_forget()
        self._center_window(self.HEIGHT_COLLAPSED)
        
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _log(self, message: str, status: Optional[Status] = None):
        """Thread-safe logging"""
        def do_log():
            self.output.configure(state="normal")
            
            prefix = {
                Status.SUCCESS: "✓  ",
                Status.ERROR: "✕  ",
                Status.WARNING: "⚠  ",
                Status.INFO: "›  ",
                Status.PROCESSING: "◌  "
            }.get(status, "   ")
            
            self.output.insert("end", f"{prefix}{message}\n")
            self.output.see("end")
            self.output.configure(state="disabled")
        
        self.ui.run_immediate(do_log)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _on_submit(self, event=None):
        """Handle command submission"""
        command = self.input_field.get().strip()
        if not command or self.is_processing:
            return
        
        self.is_processing = True
        self.input_field.delete(0, "end")
        
        # Processing animation
        self.logo.configure(text="◇")
        self.animator.pulse(self.logo, animation_id="proc")
        
        self._expand()
        self._log(command, Status.INFO)
        
        threading.Thread(
            target=self._process_command,
            args=(command,),
            daemon=True,
            name="CmdProcessor"
        ).start()
    
    def _process_command(self, command: str):
        """Process via conversation manager"""
        try:
            stop_voice()
            results = conversation_manager.process(command)
            
            for result in results:
                rtype = result.get('type')
                status = result.get('status')
                response = result.get('response', 'Done')
                
                if status == 'success':
                    self._log(response, Status.SUCCESS)
                elif status == 'error':
                    self._log(response, Status.ERROR)
                    speak(response, force=True)
                elif status == 'needs_info':
                    self._log(response, Status.WARNING)
                else:
                    self._log(response, Status.INFO)
                
                if rtype == 'function_call':
                    for f in result.get('functions_executed', []):
                        self._log(f"   → {f['function']}()", None)
                
                if status == 'success' and response:
                    speak(response)
        
        except Exception as e:
            self._log(f"Error: {e}", Status.ERROR)
            speak(str(e), force=True)
        
        finally:
            self._finish()
    
    def _finish(self):
        """Reset after processing"""
        def do_finish():
            self.is_processing = False
            self.animator.cancel("proc")
            self.logo.configure(text="⬡", text_color=THEME.accent)
        self.ui.run(do_finish)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VOICE & MIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _toggle_voice(self):
        """Toggle TTS (F12)"""
        def do_toggle():
            enabled = toggle_voice()
            self._update_voice_indicator()
            if self.is_visible:
                self._expand()
                self._log(f"Voice {'ON' if enabled else 'OFF'}", Status.INFO)
        self.ui.run_immediate(do_toggle)
    
    def _toggle_mic(self):
        """Toggle STT (F11)"""
        def do_toggle():
            if self._mic_active:
                self._mic_active = False
                stop_listening()
                self.mic_icon.configure(text_color=THEME.text_tertiary)
                self._log("Mic OFF", Status.INFO)
                return
            
            self._mic_active = True
            reset_stt()
            self.mic_icon.configure(text_color=THEME.success)
            self._expand()
            self._log("Mic ON - Listening...", Status.SUCCESS)
            self._listen_loop()
        
        self.ui.run_immediate(do_toggle)
    
    def _listen_loop(self):
        """Continuous listening"""
        def loop():
            fails = 0
            while self._mic_active:
                if is_speaking() or is_listening():
                    time.sleep(0.4)
                    continue
                
                text = listen(timeout=5)
                if text:
                    fails = 0
                    self.ui.run(lambda t=text: self._log(f"🎤 {t}", Status.SUCCESS))
                    self.ui.run(lambda: self.input_field.delete(0, "end"))
                    self.ui.run(lambda t=text: self.input_field.insert(0, t))
                    self.ui.run(self._on_submit)
                    time.sleep(2)
                else:
                    fails += 1
                    time.sleep(1.5 if fails > 3 else 0.5)
        
        threading.Thread(target=loop, daemon=True, name="Mic").start()
    
    def _stop_voice(self):
        """Stop TTS (F10)"""
        def do_stop():
            stop_voice()
            if self.is_visible:
                self._log("Stopped", Status.INFO)
        self.ui.run_immediate(do_stop)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HOTKEYS & TRAY
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _setup_hotkeys(self):
        """Register global hotkeys"""
        self.hotkeys.register("ctrl+space", self.toggle)
        self.hotkeys.register("f10", self._stop_voice)
        self.hotkeys.register("f11", self._toggle_mic)
        self.hotkeys.register("f12", self._toggle_voice)
    
    def _setup_tray(self):
        """Setup system tray"""
        if not HAS_TRAY:
            return
        self.tray = SystemTray(
            on_show=lambda: self.ui.run(self.show),
            on_quit=lambda: self.ui.run(self.quit)
        )
        self.tray.start()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def quit(self):
        """Clean shutdown"""
        if self._shutting_down:
            return
        self._shutting_down = True
        
        self.animator.cancel_all()
        self.hotkeys.unregister_all()
        
        if self.tray:
            self.tray.stop()
        
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
        os._exit(0)
    
    def run(self):
        """Start application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = SpotlightApp()
    app.run()