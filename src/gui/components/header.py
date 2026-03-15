import customtkinter as ctk
from src.gui.utils.theme import COLORS, FONTS, SIZING

class Header(ctk.CTkFrame):
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
        
        # Make the header frame draggable to move the frameless window
        self.bind("<B1-Motion>", self.app.move_window)
        self.bind("<Button-1>", self.app.get_pos)
        
        # Main Layout
        self.pack(fill="x", padx=SIZING["padding_large"], pady=(SIZING["padding_large"], SIZING["padding_small"]))
        
        # Left Side: Logo & Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(side="left", padx=SIZING["padding_regular"], pady=SIZING["padding_regular"])
        title_frame.bind("<B1-Motion>", self.app.move_window)
        title_frame.bind("<Button-1>", self.app.get_pos)
        
        # Glow title
        self.title_lbl = ctk.CTkLabel(
            title_frame,
            text="IntelliDesk AI",
            font=FONTS["h1"],
            text_color=COLORS["text_primary"]
        )
        self.title_lbl.pack(side="left")
        self.title_lbl.bind("<B1-Motion>", self.app.move_window)
        self.title_lbl.bind("<Button-1>", self.app.get_pos)
        
        # Status indicator
        self.status_lbl = ctk.CTkLabel(
            self,
            text="🟢 Ready",
            font=FONTS["body"],
            text_color=COLORS["success"]
        )
        self.status_lbl.pack(side="left", padx=20)
        self.status_lbl.bind("<B1-Motion>", self.app.move_window)
        self.status_lbl.bind("<Button-1>", self.app.get_pos)
        
        # Right Side: Window controls
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(side="right", padx=SIZING["padding_regular"])
        
        # Minimize button
        self.min_btn = ctk.CTkButton(
            controls_frame,
            text="—",
            width=30, height=30,
            fg_color="transparent",
            hover_color=COLORS["bg_glass"],
            text_color=COLORS["text_secondary"],
            font=FONTS["h2"],
            command=self.app.minimize_to_tray
        )
        self.min_btn.pack(side="left", padx=2)
        
        # Close button
        self.close_btn = ctk.CTkButton(
            controls_frame,
            text="×",
            width=30, height=30,
            fg_color="transparent",
            hover_color=COLORS["error"],
            text_color=COLORS["text_secondary"],
            font=FONTS["h2"],
            command=self.app.close_app
        )
        self.close_btn.pack(side="left", padx=2)

    def set_status(self, text, color="success"):
        self.status_lbl.configure(text=text, text_color=COLORS.get(color, COLORS["text_secondary"]))
