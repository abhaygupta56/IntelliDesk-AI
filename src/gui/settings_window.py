import customtkinter as ctk
import os
import dotenv
from pathlib import Path
from tkinter import messagebox

class SettingsWindow(ctk.CTkToplevel):
    """
    Settings interface to manage .env configuration
    """
    def __init__(self, master, ui_manager=None):
        super().__init__(master)
        
        self.title("Settings - IntelliDesk AI")
        self.geometry("500x450")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        # Load .env variables
        self.env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        dotenv.load_dotenv(self.env_path)
        
        # Main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(self.main_frame, text="Preferences", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))
        
        # Variables
        self.groq_api = ctk.StringVar(value=os.getenv("GROQ_API_KEY", ""))
        self.ollama_model = ctk.StringVar(value=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b"))
        self.ollama_url = ctk.StringVar(value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        self.voice_enabled = ctk.BooleanVar(value=os.getenv("VOICE_ENABLED", "false").lower() == "true")
        
        # Settings Sections
        self._add_label("Groq API Key:")
        ctk.CTkEntry(self.main_frame, textvariable=self.groq_api, show="*", width=350).pack(anchor="w", pady=(0, 15))
        
        self._add_label("Ollama Model:")
        ctk.CTkEntry(self.main_frame, textvariable=self.ollama_model, width=350).pack(anchor="w", pady=(0, 15))
        
        self._add_label("Ollama Base URL:")
        ctk.CTkEntry(self.main_frame, textvariable=self.ollama_url, width=350).pack(anchor="w", pady=(0, 15))
        
        ctk.CTkSwitch(self.main_frame, text="Enable Voice (TTS)", variable=self.voice_enabled).pack(anchor="w", pady=(0, 25))
        
        # Action Buttons
        save_btn = ctk.CTkButton(self.main_frame, text="Save Settings", command=self.save_settings, width=200)
        save_btn.pack(pady=20)
        
        info_lbl = ctk.CTkLabel(self.main_frame, text="Note: Saving settings might require restarting IntelliDesk.", text_color="gray", font=ctk.CTkFont(size=11))
        info_lbl.pack()
        
    def _add_label(self, text):
        ctk.CTkLabel(self.main_frame, text=text, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
    def save_settings(self):
        try:
            if not os.path.exists(self.env_path):
                with open(self.env_path, "w") as f:
                    pass
                    
            dotenv.set_key(self.env_path, "GROQ_API_KEY", self.groq_api.get())
            dotenv.set_key(self.env_path, "OLLAMA_MODEL", self.ollama_model.get())
            dotenv.set_key(self.env_path, "OLLAMA_BASE_URL", self.ollama_url.get())
            dotenv.set_key(self.env_path, "VOICE_ENABLED", "true" if self.voice_enabled.get() else "false")
            
            messagebox.showinfo("Success", "Settings saved successfully!\n\nPlease restart IntelliDesk AI for changes to take full effect.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
