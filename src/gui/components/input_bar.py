import customtkinter as ctk
from PIL import Image
from src.gui.utils.theme import COLORS, FONTS, SIZING
import os

class InputBar(ctk.CTkFrame):
    def __init__(self, master, app_ref, send_callback, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZING["radius_large"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )
        self.app = app_ref
        self.send_callback = send_callback
        
        # Load Send Icon
        send_icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "send.png")
        if os.path.exists(send_icon_path):
            self.send_img = ctk.CTkImage(light_image=Image.open(send_icon_path), size=(20, 20))
        else:
            self.send_img = None

        self.pack_propagate(False)
        self.configure(height=70)
        
        # Inner layout
        self.build_ui()
        
    def build_ui(self):
        # Voice Button (Placeholder)
        self.voice_btn = ctk.CTkButton(
            self,
            text="🎤",
            font=FONTS["h2"],
            width=50, height=50,
            fg_color="transparent",
            hover_color=COLORS["bg_glass"],
            text_color=COLORS["text_secondary"]
        )
        self.voice_btn.pack(side="left", padx=(10, 5), pady=10)
        
        # Text Input
        self.input_field = ctk.CTkEntry(
            self,
            placeholder_text="Ask me anything... (Press Enter to send)",
            font=FONTS["body_large"],
            fg_color=COLORS["bg_root"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=SIZING["radius_regular"],
            text_color=COLORS["text_primary"],
            height=50
            # Note: No focus_color in pure CTkEntry typically, simulated by binding
        )
        self.input_field.pack(side="left", fill="both", expand=True, pady=10)
        
        self.input_field.bind("<FocusIn>", self.on_focus)
        self.input_field.bind("<FocusOut>", self.on_unfocus)
        self.input_field.bind("<Return>", lambda e: self.trigger_send())
        
        # Send Button 
        self.send_btn = ctk.CTkButton(
            self,
            text="" if self.send_img else "→",
            image=self.send_img,
            width=50, height=50,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            corner_radius=SIZING["radius_regular"],
            command=self.trigger_send
        )
        self.send_btn.pack(side="right", padx=(5, 10), pady=10)
        
    def on_focus(self, event):
        self.input_field.configure(border_color=COLORS["accent_primary"])
        
    def on_unfocus(self, event):
        self.input_field.configure(border_color=COLORS["border"])
        
    def trigger_send(self):
        text = self.input_field.get().strip()
        if text:
            self.input_field.delete(0, "end")
            self.send_callback(text)
            
    def set_and_send(self, text):
        self.input_field.delete(0, "end")
        self.input_field.insert(0, text)
        self.trigger_send()
