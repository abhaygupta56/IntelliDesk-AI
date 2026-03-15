import customtkinter as ctk
from src.gui.utils.theme import COLORS, FONTS, SIZING

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, app_ref, **kwargs):
        super().__init__(
            master, 
            fg_color=COLORS["bg_card"],
            corner_radius=SIZING["radius_regular"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )
        self.app = app_ref
        
        # Setup UI
        self.build_ui()
        
    def build_ui(self):
        # Stats Section
        stats_lbl = ctk.CTkLabel(
            self, 
            text="Quick Commands", 
            font=FONTS["h2"],
            text_color=COLORS["text_primary"]
        )
        stats_lbl.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Quick Actions
        actions = [
            ("📸 Screenshot", "screenshot"),
            ("⏰ Time", "time"),
            ("🔒 Lock PC", "lock pc"),
            ("🎵 Play Music", "play"),
        ]
        
        for text, cmd in actions:
            btn = ctk.CTkButton(
                self,
                text=text,
                font=FONTS["body"],
                fg_color=COLORS["bg_glass"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_primary"],
                anchor="w",
                height=40,
                command=lambda c=cmd: self.app.input_bar.set_and_send(c)
            )
            btn.pack(fill="x", padx=15, pady=5)
            
        # Stats display
        ctk.CTkLabel(
            self,
            text="Live Stats",
            font=FONTS["h2"],
            text_color=COLORS["text_primary"]
        ).pack(pady=(30, 10), padx=20, anchor="w")
        
        self.stats_text = ctk.CTkTextbox(
            self,
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"],
            height=120,
            wrap="word",
            state="disabled"
        )
        self.stats_text.pack(fill="x", padx=15, pady=5)
        
    def update_stats(self, stats_data):
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")
        
        msg = (
            f"Pattern Matches: {stats_data.get('pattern', 0)} ({stats_data.get('pattern_ratio', 0)}%)\n"
            f"AI Matches: {stats_data.get('ai', 0)}\n"
            f"Total Run: {stats_data.get('total', 0)}\n"
            f"Tokens Saved: ~{stats_data.get('tokens_saved', 0)}"
        )
        
        self.stats_text.insert("end", msg)
        self.stats_text.configure(state="disabled")
