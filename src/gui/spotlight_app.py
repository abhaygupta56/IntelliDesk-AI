"""
IntelliDesk AI - Spotlight App
Premium Glassmorphic Command Palette
Merged: new warm-indigo GUI + full production logic
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
import math
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════
from src.core.conversation_manager import conversation_manager
from src.core.agentic_manager import agentic_manager
from src.core.function_registry import FunctionRegistry
from src.core.router import router, MODE_AUTO, MODE_CHAT, MODE_AGENT
from src.utils.voice_manager import toggle_voice, is_voice_enabled, speak, stop_voice, is_speaking
from src.utils.stt_manager import listen_async, is_listening, listen, stop_listening, reset_stt
from config import Config

# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
IS_WINDOWS = sys.platform == "win32"
IS_MAC     = sys.platform == "darwin"
IS_LINUX   = sys.platform.startswith("linux")

keyboard = None
if IS_WINDOWS:
    try:
        import keyboard
    except ImportError:
        print("⚠ 'keyboard' module not found. Global hotkeys disabled.")

HAS_TRAY = False
pystray  = None
Image    = None
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
# PREMIUM GLASSMORPHIC THEME  (warm dark, indigo/violet undertones)
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Theme:
    # Glass layers
    glass_primary:   str = "#111116"
    glass_elevated:  str = "#1a1a24"
    glass_surface:   str = "#222230"

    # Borders
    border_subtle:   str = "#2a2a38"
    border_inner:    str = "#353548"
    border_glow:     str = "#434371"

    # Text hierarchy
    text_primary:    str = "#f8fafc"
    text_secondary:  str = "#cbd5e1"
    text_tertiary:   str = "#64748b"
    text_placeholder:str = "#475569"

    # Accent
    accent:          str = "#818cf8"
    accent_soft:     str = "#6366f1"

    # Semantic
    success:         str = "#6ee7b7"
    warning:         str = "#fcd34d"
    error:           str = "#fca5a5"
    info:            str = "#93c5fd"


THEME = Theme()

FONT_DISPLAY = ("Segoe UI Variable Display", 16)
FONT_BODY    = ("Segoe UI Variable Text",    14)
FONT_MONO    = ("JetBrains Mono",            16)
FONT_LOG     = ("Cascadia Code",             13)
FONT_HINT    = ("Segoe UI Variable Small",   10, "bold")


class Status(Enum):
    SUCCESS    = "success"
    ERROR      = "error"
    WARNING    = "warning"
    INFO       = "info"
    NEEDS_INFO = "needs_info"
    PROCESSING = "processing"


# ═══════════════════════════════════════════════════════════════════════════════
# THREAD-SAFE UI UPDATER
# ═══════════════════════════════════════════════════════════════════════════════
class ThreadSafeUI:
    def __init__(self, root: ctk.CTk):
        self.root  = root
        self.queue: queue.Queue[Callable] = queue.Queue()
        self._poll()

    def _poll(self):
        try:
            while True:
                cb = self.queue.get_nowait()
                try:
                    cb()
                except Exception as e:
                    import logging
                    logging.getLogger("ThreadSafeUI").error(f"UI callback failed: {e}", exc_info=True)
        except queue.Empty:
            pass
        finally:
            self.root.after(10, self._poll)

    def run(self, cb: Callable):
        self.queue.put(cb)

    def run_immediate(self, cb: Callable):
        if threading.current_thread() is threading.main_thread():
            cb()
        else:
            self.queue.put(cb)


# ═══════════════════════════════════════════════════════════════════════════════
# SMOOTH ANIMATOR
# ═══════════════════════════════════════════════════════════════════════════════
def hex_to_rgb(hex_color: str):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"


class Animator:
    def __init__(self, root: ctk.CTk):
        self.root    = root
        self._active: Dict[str, bool] = {}

    def cancel(self, animation_id: str):
        self._active[animation_id] = False

    def cancel_all(self):
        for key in self._active:
            self._active[key] = False

    # ── slide + fade in (new GUI entrance animation) ────────────────────────
    def slide_fade_in(self, target_y: int, duration_ms: int = 250, offset: int = 12,
                      on_complete: Optional[Callable] = None):
        animation_id = "slide_fade"
        self.cancel(animation_id)
        self._active[animation_id] = True

        steps = max(1, duration_ms // 10)
        delay = duration_ms // steps
        start_y = target_y - offset

        geo = self.root.geometry()
        try:
            w_h, *x_y = geo.split('+')
            x = int(x_y[0])
            w, h = map(int, w_h.split('x'))
        except Exception:
            return

        def animate(step: int):
            if not self._active.get(animation_id, False):
                return
            if step <= steps:
                t     = step / steps
                ease  = 1 - pow(1 - t, 3)          # ease-out cubic
                cur_y = int(start_y + offset * ease)
                try:
                    self.root.attributes("-alpha", ease)
                    self.root.geometry(f"{w}x{h}+{x}+{cur_y}")
                except Exception:
                    pass
                self.root.after(delay, animate, step + 1)
            else:
                self._active[animation_id] = False
                try:
                    self.root.attributes("-alpha", 1.0)
                    self.root.geometry(f"{w}x{h}+{x}+{target_y}")
                except Exception:
                    pass
                if on_complete:
                    on_complete()

        self.root.attributes("-alpha", 0.0)
        self.root.geometry(f"{w}x{h}+{x}+{start_y}")
        animate(1)

    # ── fade out ────────────────────────────────────────────────────────────
    def fade_out(self, duration_ms: int = 160, on_complete: Optional[Callable] = None):
        animation_id = "fade_out"
        self.cancel(animation_id)
        self._active[animation_id] = True

        steps = max(1, duration_ms // 8)
        delay = duration_ms // steps

        def animate(step: int):
            if not self._active.get(animation_id, False):
                return
            if step <= steps:
                t = step / steps
                try:
                    self.root.attributes("-alpha", 1 - t * t)
                except Exception:
                    pass
                self.root.after(delay, animate, step + 1)
            else:
                self._active[animation_id] = False
                if on_complete:
                    on_complete()

        animate(1)

    # ── smooth color interpolation ──────────────────────────────────────────
    def lerp_color(self, widget, property_name: str,
                   start_hex: str, end_hex: str, duration_ms: int = 200):
        animation_id = f"color_{id(widget)}_{property_name}"
        self.cancel(animation_id)
        self._active[animation_id] = True

        c1    = hex_to_rgb(start_hex)
        c2    = hex_to_rgb(end_hex)
        steps = max(1, duration_ms // 16)
        delay = duration_ms // steps

        def animate(step: int):
            if not self._active.get(animation_id, False):
                return
            try:
                if not widget.winfo_exists():
                    return
            except Exception:
                return

            if step <= steps:
                t = step / steps
                cur = rgb_to_hex(tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3)))
                try:
                    widget.configure(**{property_name: cur})
                except Exception:
                    pass
                self.root.after(delay, animate, step + 1)
            else:
                self._active[animation_id] = False
                try:
                    widget.configure(**{property_name: end_hex})
                except Exception:
                    pass

        animate(1)

    # ── pulsing color (kept for mic indicator) ──────────────────────────────
    def pulse(self, label: ctk.CTkLabel,
              colors: tuple = (THEME.accent, THEME.text_tertiary),
              interval_ms: int = 450, animation_id: str = "pulse"):
        self._active[animation_id] = True

        def animate(index: int):
            if not self._active.get(animation_id, False):
                return
            try:
                label.configure(text_color=colors[index % len(colors)])
            except Exception:
                return
            self.root.after(interval_ms, animate, index + 1)

        animate(0)


# ═══════════════════════════════════════════════════════════════════════════════
# WINDOWS ACRYLIC BLUR
# ═══════════════════════════════════════════════════════════════════════════════
class WindowsEffects:
    @staticmethod
    def apply_blur(root: ctk.CTk) -> bool:
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
    def __init__(self, on_show: Callable, on_quit: Callable,
                 app_name: str = "IntelliDesk AI"):
        self.on_show  = on_show
        self.on_quit  = on_quit
        self.app_name = app_name
        self.icon: Optional[pystray.Icon] = None
        self._running = False

    def _create_icon(self) -> 'Image.Image':
        size = 64
        img  = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([6, 6, size - 6, size - 6], radius=14,
                                fill=(129, 140, 248, 255))   # indigo accent
        cx, cy, r = size // 2, size // 2, 15
        pts = [(cx + r * math.cos(math.pi / 3 * i - math.pi / 2),
                cy + r * math.sin(math.pi / 3 * i - math.pi / 2)) for i in range(6)]
        draw.polygon(pts, fill=(255, 255, 255, 255))
        return img

    def start(self):
        if not HAS_TRAY or self._running:
            return
        menu = pystray.Menu(
            TrayMenuItem('Show (Ctrl+Space)', lambda: self.on_show(), default=True),
            pystray.Menu.SEPARATOR,
            TrayMenuItem('Quit', lambda: self.on_quit())
        )
        self.icon     = pystray.Icon("IntelliDesk", self._create_icon(),
                                     self.app_name, menu)
        self._running = True
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon and self._running:
            self._running = False
            try:
                self.icon.stop()
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
# HOTKEY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════
class HotkeyManager:
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
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# COLLAPSIBLE DETAILS PANEL (for technical logs)
# ═══════════════════════════════════════════════════════════════════════════════
class CollapsibleDetails(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.is_expanded = False
        
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", pady=(2, 2))
        
        self.toggle_btn = ctk.CTkButton(
            self.header,
            text="▶ System logs & details",
            font=ctk.CTkFont(family=FONT_LOG[0], size=FONT_LOG[1] - 1),
            fg_color="transparent",
            text_color=THEME.text_tertiary,
            hover_color=THEME.glass_elevated,
            anchor="w",
            height=22,
            width=180,
            command=self.toggle
        )
        self.toggle_btn.pack(side="left", padx=12)
        
        self.content = ctk.CTkFrame(
            self,
            fg_color=THEME.glass_surface,
            corner_radius=10,
            border_width=1,
            border_color=THEME.border_subtle
        )
        
    def toggle(self):
        if self.is_expanded:
            self.content.pack_forget()
            self.toggle_btn.configure(text="▶ System logs & details")
            self.is_expanded = False
        else:
            self.content.pack(fill="x", padx=(28, 16), pady=(2, 6))
            self.toggle_btn.configure(text="▼ System logs & details")
            self.is_expanded = True
            
        try:
            self.master._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# SPOTLIGHT APP — PREMIUM COMMAND PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
class SpotlightApp:
    WIDTH            = 840
    HEIGHT_COLLAPSED = 76     # taller to fit larger input row
    HEIGHT_EXPANDED  = 620
    CORNER_RADIUS    = 24

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("IntelliDesk AI")
        self.root.withdraw()

        # ── State ────────────────────────────────────────────────────────────
        self.is_visible    = False
        self.is_expanded   = False
        self.is_processing = False
        self._shutting_down = False
        self.voice_enabled = is_voice_enabled()
        self._mic_active   = False
        self.target_y      = 0
        self.current_details: Optional[CollapsibleDetails] = None

        # ── Core systems ─────────────────────────────────────────────────────
        self.ui       = ThreadSafeUI(self.root)
        self.animator = Animator(self.root)
        self.hotkeys  = HotkeyManager()
        self.tray: Optional[SystemTray] = None

        # ── Build ────────────────────────────────────────────────────────────
        self._configure_window()
        self._build_ui()
        self._bind_events()
        self._setup_hotkeys()
        self._setup_tray()

        # Register thread-safe confirmation dispatcher
        FunctionRegistry.register_confirm_dispatcher(self._dangerous_action_confirm)

        self.root.after(100, self._apply_effects)
        self.root.after(180, self.show)

    # ═══════════════════════════════════════════════════════════════════════════
    # WINDOW CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════

    def _configure_window(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0)
        self.root.configure(fg_color=THEME.glass_primary, padx=0, pady=0)
        self._center_window(self.HEIGHT_COLLAPSED)

    def _center_window(self, height: int):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - self.WIDTH) // 2
        self.target_y = (sh - height) // 2 - 80
        self.root.geometry(f"{self.WIDTH}x{height}+{x}+{self.target_y}")

    def _apply_effects(self):
        if IS_WINDOWS:
            WindowsEffects.apply_blur(self.root)

    # ═══════════════════════════════════════════════════════════════════════════
    # UI BUILDING
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        # Main glass container with glow border
        self.glass = ctk.CTkFrame(
            self.root,
            fg_color=THEME.glass_primary,
            corner_radius=self.CORNER_RADIUS,
            border_width=1,
            border_color=THEME.border_glow
        )
        self.glass.pack(fill="both", expand=True)

        # ── Input row ────────────────────────────────────────────────────────
        self.input_row = ctk.CTkFrame(self.glass, fg_color="transparent", height=60)
        self.input_row.pack(fill="x", padx=16, pady=(12, 10))
        self.input_row.pack_propagate(False)

        self.logo = ctk.CTkLabel(
            self.input_row, text="⬡",
            font=ctk.CTkFont(family="Segoe UI Symbol", size=28, weight="bold"),
            text_color=THEME.accent, width=40
        )
        self.logo.pack(side="left", padx=(8, 12))

        self.voice_icon = ctk.CTkLabel(
            self.input_row, text="🔈",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=14),
            text_color=THEME.text_tertiary, width=24
        )
        self.voice_icon.pack(side="left", padx=(0, 6))
        self._update_voice_indicator()

        self.mic_icon = ctk.CTkLabel(
            self.input_row, text="🎙",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=14),
            text_color=THEME.text_tertiary, width=24
        )
        self.mic_icon.pack(side="left", padx=(0, 12))

        # Hero input field
        self.input_field = ctk.CTkEntry(
            self.input_row,
            placeholder_text="Ask anything, run anything...",
            font=ctk.CTkFont(*FONT_MONO),
            fg_color=THEME.glass_elevated,
            border_width=1,
            border_color=THEME.border_inner,
            corner_radius=14,
            text_color=THEME.text_primary,
            placeholder_text_color=THEME.text_placeholder,
            height=44
        )
        self.input_field.pack(side="left", fill="both", expand=True, padx=(0, 12))

        # Focus animations on the entry border
        self.input_field.bind(
            "<FocusIn>",
            lambda e: self.animator.lerp_color(
                self.input_field, "border_color", THEME.border_inner, THEME.border_glow, 200)
        )
        self.input_field.bind(
            "<FocusOut>",
            lambda e: self.animator.lerp_color(
                self.input_field, "border_color", THEME.border_glow, THEME.border_inner, 200)
        )

        # Mode pill
        self.mode_pill = ctk.CTkFrame(
            self.input_row, fg_color=THEME.glass_surface,
            corner_radius=10, border_width=1, border_color=THEME.border_subtle
        )
        self.mode_pill.pack(side="left", padx=(0, 10))

        self._mode_buttons: Dict[str, ctk.CTkButton] = {}
        mode_defs = [
            (MODE_AUTO,  "Auto",  "🔀"),
            (MODE_CHAT,  "Chat",  "💬"),
            (MODE_AGENT, "Agent", "🤖"),
        ]
        for mode_key, label, icon in mode_defs:
            btn = ctk.CTkButton(
                self.mode_pill,
                text=f"{icon} {label}",
                font=ctk.CTkFont(*FONT_HINT),
                fg_color="transparent",
                hover_color=THEME.glass_elevated,
                text_color=THEME.text_tertiary,
                corner_radius=8,
                width=58, height=28,
                command=lambda m=mode_key: self._set_mode(m)
            )
            btn.pack(side="left", padx=3, pady=3)
            self._mode_buttons[mode_key] = btn

        # Keyboard hints (right side)
        self.hints = ctk.CTkFrame(self.input_row, fg_color="transparent")
        self.hints.pack(side="right", padx=(0, 6))
        for i, key in enumerate(["↵", "F11", "F12", "Esc"]):
            self._create_hint(self.hints, key).pack(side="left", padx=3)
            if i < 3:
                ctk.CTkLabel(
                    self.hints, text="·",
                    text_color=THEME.text_tertiary,
                    font=ctk.CTkFont(*FONT_HINT)
                ).pack(side="left", padx=1)

        # ── Results panel (hidden initially) ─────────────────────────────────
        self.results = ctk.CTkFrame(self.glass, fg_color="transparent")

        # Log header with mode + timestamp
        self.log_header = ctk.CTkFrame(self.results, fg_color="transparent", height=24)
        self.log_header.pack(fill="x", padx=20, pady=(0, 4))

        self.mode_label = ctk.CTkLabel(
            self.log_header, text="Mode: Auto",
            text_color=THEME.text_tertiary, font=ctk.CTkFont(*FONT_HINT)
        )
        self.mode_label.pack(side="left")

        self.time_label = ctk.CTkLabel(
            self.log_header, text="",
            text_color=THEME.text_tertiary, font=ctk.CTkFont(*FONT_HINT)
        )
        self.time_label.pack(side="right")

        # Glow separator
        sep_container = ctk.CTkFrame(self.results, fg_color="transparent", height=1)
        sep_container.pack(fill="x", padx=20, pady=(0, 10))
        sep_container.pack_propagate(False)
        ctk.CTkFrame(sep_container, fg_color=THEME.border_glow, height=1).pack(
            fill="x", expand=True, padx=40
        )

        # Scrollable output log
        self.output = ctk.CTkScrollableFrame(
            self.results,
            fg_color=THEME.glass_elevated,
            corner_radius=14,
            border_width=1,
            border_color=THEME.border_inner,
            height=480
        )
        self.output.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        self._set_mode(MODE_AUTO)

    def _create_hint(self, parent, key: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(
            frame, text=key,
            font=ctk.CTkFont(*FONT_HINT),
            fg_color=THEME.glass_surface, corner_radius=6,
            text_color=THEME.text_tertiary,
            width=24 if len(key) <= 2 else 32, height=18
        ).pack(side="left")
        return frame

    def _set_mode(self, mode: str):
        router.mode = mode
        colours = {MODE_AUTO: THEME.accent, MODE_CHAT: THEME.success, MODE_AGENT: THEME.warning}
        self.mode_label.configure(text=f"Mode: {mode.capitalize()}")

        for key, btn in self._mode_buttons.items():
            if key == mode:
                self.animator.lerp_color(btn, "fg_color", THEME.glass_surface, THEME.border_glow, 200)
                btn.configure(text_color=colours[key])
            else:
                self.animator.lerp_color(btn, "fg_color", THEME.glass_elevated, THEME.glass_surface, 150)
                btn.configure(text_color=THEME.text_tertiary)

    def _update_voice_indicator(self):
        if is_voice_enabled():
            self.voice_icon.configure(text="🔊", text_color=THEME.success)
        else:
            self.voice_icon.configure(text="🔈", text_color=THEME.text_tertiary)

    # ═══════════════════════════════════════════════════════════════════════════
    # EVENT BINDING
    # ═══════════════════════════════════════════════════════════════════════════

    def _bind_events(self):
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
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════════════════
    # SHOW / HIDE / TOGGLE
    # ═══════════════════════════════════════════════════════════════════════════

    def show(self):
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

        # Use the new slide-fade-in entrance
        self.animator.slide_fade_in(target_y=self.target_y, duration_ms=250, offset=12)

    def hide(self):
        if not self.is_visible or self._shutting_down:
            return
        self.is_visible = False
        self.animator.cancel_all()

        def on_complete():
            self.root.withdraw()
            self._collapse()
            self.input_field.delete(0, "end")

        self.animator.fade_out(160, on_complete=on_complete)

    def toggle(self):
        self.ui.run_immediate(self._toggle_internal)

    def _toggle_internal(self):
        self.hide() if self.is_visible else self.show()

    # ═══════════════════════════════════════════════════════════════════════════
    # EXPAND / COLLAPSE
    # ═══════════════════════════════════════════════════════════════════════════

    def _expand(self):
        if self.is_expanded:
            return
        self.is_expanded = True
        self.results.pack(fill="both", expand=True)
        self._center_window(self.HEIGHT_EXPANDED)

    def _collapse(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        self.results.pack_forget()
        self._center_window(self.HEIGHT_COLLAPSED)
        for child in self.output.winfo_children():
            child.destroy()
        self.current_details = None

    # ═══════════════════════════════════════════════════════════════════════════
    # LOGGING  (new styled bubbles from new GUI)
    # ═══════════════════════════════════════════════════════════════════════════

    def _log(self, message: str, status: Optional[Status] = None):
        """Thread-safe styled logging."""
        def do_log():
            is_technical = (status == Status.PROCESSING or status is None) and self.is_processing
            
            if is_technical:
                if self.current_details is None:
                    self.current_details = CollapsibleDetails(self.output)
                    self.current_details.pack(fill="x", padx=6, pady=4)
                parent = self.current_details.content
            else:
                parent = self.output

            container = ctk.CTkFrame(parent, fg_color="transparent")
            container.pack(fill="x", padx=6, pady=4)

            if status == Status.INFO:
                # User command bubble
                msg_frame = ctk.CTkFrame(container, fg_color=THEME.glass_surface, corner_radius=10)
                msg_frame.pack(side="left", padx=4, pady=4)
                ctk.CTkLabel(
                    msg_frame, text=message,
                    text_color=THEME.text_primary,
                    font=ctk.CTkFont(family=FONT_LOG[0], size=FONT_LOG[1], weight="bold"),
                    justify="left", wraplength=680
                ).pack(padx=12, pady=8)

            elif status == Status.SUCCESS:
                # AI response — plain readable text
                ctk.CTkLabel(
                    container, text=message,
                    text_color=THEME.text_secondary,
                    font=ctk.CTkFont(*FONT_LOG),
                    justify="left", wraplength=700
                ).pack(side="left", padx=16, pady=4)

            elif status in (Status.WARNING, Status.NEEDS_INFO):
                # Accent strip left, warning colour
                color = THEME.warning
                ctk.CTkFrame(container, fg_color=color, width=3, corner_radius=2).pack(
                    side="left", fill="y", padx=(4, 8), pady=2
                )
                ctk.CTkLabel(
                    container, text=message,
                    text_color=color,
                    font=ctk.CTkFont(*FONT_LOG),
                    justify="left", wraplength=690
                ).pack(side="left", pady=4)

            elif status == Status.ERROR:
                color = THEME.error
                ctk.CTkFrame(container, fg_color=color, width=3, corner_radius=2).pack(
                    side="left", fill="y", padx=(4, 8), pady=2
                )
                ctk.CTkLabel(
                    container, text=message,
                    text_color=color,
                    font=ctk.CTkFont(*FONT_LOG),
                    justify="left", wraplength=690
                ).pack(side="left", pady=4)

            elif status == Status.PROCESSING:
                # Dimmed system note
                ctk.CTkLabel(
                    container, text=message,
                    text_color=THEME.text_tertiary,
                    font=ctk.CTkFont(*FONT_LOG),
                    justify="left"
                ).pack(side="left", padx=16, pady=4)

            else:
                # Default: function call traces, misc notes
                # Support multi-line / long code via a Textbox
                lines       = message.split("\n")
                line_count  = len(lines)
                max_line_len = max((len(L) for L in lines), default=0)

                if line_count > 1 or max_line_len > 80:
                    box_height = min(400, line_count * 18 + 10)
                    box = ctk.CTkTextbox(
                        container,
                        fg_color="transparent",
                        text_color=THEME.text_tertiary,
                        font=ctk.CTkFont(family=FONT_LOG[0], size=FONT_LOG[1]),
                        wrap="word",
                        height=box_height
                    )
                    box.pack(side="left", fill="x", expand=True, padx=16)
                    box.insert("end", message)
                    box.configure(state="disabled")
                else:
                    ctk.CTkLabel(
                        container, text=message,
                        text_color=THEME.text_tertiary,
                        font=ctk.CTkFont(*FONT_LOG),
                        justify="left"
                    ).pack(side="left", padx=16, pady=4)

            # Auto-scroll
            try:
                self.output._parent_canvas.yview_moveto(1.0)
            except Exception:
                pass

        self.ui.run_immediate(do_log)

    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════

    def _on_submit(self, event=None):
        command = self.input_field.get().strip()
        if not command or self.is_processing:
            return

        self.is_processing = True
        self.current_details = None
        self.input_field.delete(0, "end")

        # Stamp the timestamp on the log header
        self.time_label.configure(text=datetime.datetime.now().strftime("%H:%M"))

        self._animate_spinner()
        self._expand()
        self._log(command, Status.INFO)

        threading.Thread(
            target=self._process_command,
            args=(command,),
            daemon=True,
            name="CmdProcessor"
        ).start()

    def _animate_spinner(self, idx: int = 0):
        """Braille-style spinning logo while processing."""
        if not self.is_processing:
            return
        frames = ['◐', '◓', '◑', '◒']
        self.logo.configure(text=frames[idx % len(frames)], text_color=THEME.accent)
        self.root.after(120, self._animate_spinner, idx + 1)

    def _process_command(self, command: str):
        """Process via SmartRouter — auto-dispatches to Chat or Agent."""
        try:
            stop_voice()

            # Show effective mode hint when in Auto
            effective   = router.effective_mode_for(command)
            mode_labels = {MODE_AUTO: "🔀 Auto", MODE_CHAT: "💬 Chat", MODE_AGENT: "🤖 Agent", "code_gen": "💻 Code"}
            if router.mode == MODE_AUTO:
                self._log(f"{mode_labels[effective]} mode detected", Status.PROCESSING)

            results = router.process(command)

            for result in results:
                rtype    = result.get('type')
                status   = result.get('status')
                response = result.get('response', 'Done')
                data     = result.get('data', {})

                if status == 'success':
                    self._log(response, Status.SUCCESS)
                    if data and 'code' in data:
                        self._log(data['code'], None)
                        if data.get('filepath'):
                            self._log(f"Saved to: {data['filepath']}", Status.PROCESSING)
                elif status == 'error':
                    self._log(response, Status.ERROR)
                    speak(response, force=True)
                elif status == 'needs_info':
                    self._log(response, Status.NEEDS_INFO)
                else:
                    self._log(response, Status.PROCESSING)

                if result.get('functions_executed'):
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
        """Reset logo + processing flag after a command completes."""
        def do_finish():
            self.is_processing = False
            # Brief success flash then back to idle hex
            self.logo.configure(text="✦", text_color=THEME.success)
            self.root.after(600, lambda: self.logo.configure(text="⬡", text_color=THEME.accent))
        self.ui.run(do_finish)

    # ═══════════════════════════════════════════════════════════════════════════
    # DANGEROUS ACTION CONFIRMATION  (thread-safe)
    # ═══════════════════════════════════════════════════════════════════════════

    def _dangerous_action_confirm(self, title: str, text: str) -> bool:
        """Always runs the dialog on the Tkinter main thread."""
        from tkinter import messagebox
        result_holder = [False]
        done = threading.Event()

        def show_dialog():
            result_holder[0] = messagebox.askyesno(title, text, icon="warning")
            done.set()

        self.ui.run_immediate(show_dialog)
        done.wait(timeout=60)
        return result_holder[0]

    # ═══════════════════════════════════════════════════════════════════════════
    # VOICE & MIC
    # ═══════════════════════════════════════════════════════════════════════════

    def _toggle_voice(self):
        """Toggle TTS (F12)."""
        def do_toggle():
            enabled = toggle_voice()
            self._update_voice_indicator()
            if self.is_visible:
                self._expand()
                self._log(f"Voice {'ON' if enabled else 'OFF'}", Status.PROCESSING)
        self.ui.run_immediate(do_toggle)

    def _toggle_mic(self):
        """Toggle STT (F11)."""
        def do_toggle():
            if self._mic_active:
                self._mic_active = False
                stop_listening()
                self.mic_icon.configure(text_color=THEME.text_tertiary)
                self._log("Mic OFF", Status.PROCESSING)
                return

            self._mic_active = True
            reset_stt()
            self.mic_icon.configure(text_color=THEME.success)
            self._expand()
            self._log("Mic ON — Listening...", Status.SUCCESS)
            self._listen_loop()

        self.ui.run_immediate(do_toggle)

    def _listen_loop(self):
        """Continuous STT loop."""
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
        """Stop TTS immediately (F10)."""
        def do_stop():
            stop_voice()
            if self.is_visible:
                self._log("Speech stopped", Status.PROCESSING)
        self.ui.run_immediate(do_stop)

    # ═══════════════════════════════════════════════════════════════════════════
    # HOTKEYS & TRAY
    # ═══════════════════════════════════════════════════════════════════════════

    def _setup_hotkeys(self):
        self.hotkeys.register("ctrl+space", self.toggle)
        self.hotkeys.register("f10",        self._stop_voice)
        self.hotkeys.register("f11",        self._toggle_mic)
        self.hotkeys.register("f12",        self._toggle_voice)

    def _setup_tray(self):
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
        except Exception:
            pass

        os._exit(0)

    def run(self):
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