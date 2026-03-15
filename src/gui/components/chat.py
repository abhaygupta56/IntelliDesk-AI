import customtkinter as ctk
from src.gui.utils.theme import COLORS, FONTS, SIZING
import datetime

class ChatMessage(ctk.CTkFrame):
    def __init__(self, master, text, is_user=False, **kwargs):
        bg_color = COLORS["chat_user"] if is_user else COLORS["chat_bot"]
        super().__init__(
            master,
            fg_color=bg_color,
            corner_radius=SIZING["radius_regular"],
            **kwargs
        )
        
        # Border for bot messages to look more premium glass
        if not is_user:
            self.configure(border_width=1, border_color=COLORS["border"])
            
        self.is_user = is_user
        
        # Header (Name + Time)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 5))
        
        name = "🎯 You" if is_user else "🤖 IntelliDesk AI"
        name_color = COLORS["accent_primary"] if is_user else COLORS["success"]
        time_str = datetime.datetime.now().strftime("%H:%M")
        
        name_lbl = ctk.CTkLabel(
            header_frame, 
            text=name, 
            font=FONTS["body_small"],
            text_color=name_color
        )
        name_lbl.pack(side="left")
        
        time_lbl = ctk.CTkLabel(
            header_frame, 
            text=time_str, 
            font=FONTS["body_small"],
            text_color=COLORS["text_muted"]
        )
        time_lbl.pack(side="right")
        
        # Message Text
        # Using a CTkTextbox for text selection / copying
        self.msg_box = ctk.CTkTextbox(
            self,
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
            wrap="word",
            height=10 # Dynamic resize logic needed, estimating for now
        )
        self.msg_box.insert("1.0", text)
        self.msg_box.configure(state="disabled")
        
        # Calculate dynamic height
        lines = text.count('\\n') + 1 + (len(text) // 60)
        self.msg_box.configure(height=lines * 22 + 10)
        
        self.msg_box.pack(fill="x", expand=True, padx=12, pady=(0, 12))

class ChatArea(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZING["radius_regular"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )
        
        # Container to hold bubbles with expanding space
        self.msg_container = ctk.CTkFrame(self, fg_color="transparent")
        self.msg_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.messages = []
        
    def add_message(self, text, is_user=False):
        # Outer frame for alignment (right/left)
        align_frame = ctk.CTkFrame(self.msg_container, fg_color="transparent")
        align_frame.pack(fill="x", pady=5)
        
        msg = ChatMessage(align_frame, text, is_user=is_user)
        
        if is_user:
            msg.pack(side="right", fill="x", expand=False, padx=(50, 0))
        else:
            msg.pack(side="left", fill="x", expand=False, padx=(0, 50))
            
        self.messages.append(msg)
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1.0) # Scroll to bottom
    
    def add_typing_indicator(self):
        # Placeholder for dynamic dots animation
        self.typing_msg = ChatMessage(self.msg_container, "● ● ●", is_user=False)
        self.typing_msg.pack(side="left", fill="x", pady=5, padx=(0, 50))
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1.0)
        
    def remove_typing_indicator(self):
        if hasattr(self, 'typing_msg'):
            self.typing_msg.destroy()
            del self.typing_msg
