"""
Function Registry - Smart grouped loading for performance
"""

from src.automation import system_ops, utility_ops, keyboard_ops, window_ops, file_ops, web_ops, media_ops, reminder_ops, email_ops
from src.automation import whatsapp as whatsapp_ops
from src.automation import sentry_mode


class FunctionRegistry:
    """Smart function registry with grouped loading"""
    
    def __init__(self):
        self.all_functions = self._build_all_functions()
        self.core_functions = self._get_core_functions()
    
    def _build_all_functions(self):
        """All 62 functions organized by category"""
        return {
            # ═══════════════════════════════════════════════════════════
            # CORE - Always loaded (most common)
            # ═══════════════════════════════════════════════════════════
            "core": [
                {
                    "name": "open_app",
                    "description": "Open any application",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "Application name"}
                        },
                        "required": ["app_name"]
                    },
                    "function": system_ops.open_app
                },
                {
                    "name": "get_time",
                    "description": "Get current time",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": utility_ops.get_time
                },
                {
                    "name": "get_date",
                    "description": "Get current date",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": utility_ops.get_date
                },
                {
                    "name": "calculate",
                    "description": "Calculate math expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "Math expression"}
                        },
                        "required": ["expression"]
                    },
                    "function": utility_ops.calculate
                },
                {
                    "name": "type_text",
                    "description": "Type text using keyboard",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to type"}
                        },
                        "required": ["text"]
                    },
                    "function": keyboard_ops.type_text
                },
                {
                    "name": "flip_coin",
                    "description": "Flip a coin",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": utility_ops.flip_coin
                },
                {
                    "name": "screenshot",
                    "description": "Take screenshot",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.screenshot
                },
                {
                    "name": "volume_up",
                    "description": "Increase volume",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.volume_up
                },
                {
                    "name": "volume_down",
                    "description": "Decrease volume",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.volume_down
                },
                {
                    "name": "close_app",
                    "description": "Close application",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "Application name"}
                        },
                        "required": ["app_name"]
                    },
                    "function": system_ops.close_app
                },
            ],
            
            # ═══════════════════════════════════════════════════════════
            # SYSTEM - Load when user mentions: lock, shutdown, restart, sleep
            # ═══════════════════════════════════════════════════════════
            "system": [
                {
                    "name": "lock_system",
                    "description": "Lock computer",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.lock
                },
                {
                    "name": "shutdown_system",
                    "description": "Shutdown computer",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.shutdown
                },
                {
                    "name": "restart_system",
                    "description": "Restart computer",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.restart
                },
                {
                    "name": "sleep_system",
                    "description": "Put computer to sleep",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.sleep
                },
                {
                    "name": "get_system_info",
                    "description": "Get system information",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.system_info
                },
                {
                    "name": "brightness_up",
                    "description": "Increase brightness",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.brightness_up
                },
                {
                    "name": "brightness_down",
                    "description": "Decrease brightness",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": system_ops.brightness_down
                },
            ],
            
            # ═══════════════════════════════════════════════════════════
            # WEB - Load when: search, youtube, google, wikipedia, weather
            # ═══════════════════════════════════════════════════════════
            "web": [
                {
                    "name": "google_search",
                    "description": "Search Google",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    },
                    "function": web_ops.google
                },
                {
                    "name": "youtube_search",
                    "description": "Search YouTube",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    },
                    "function": web_ops.youtube
                },
                {
                    "name": "play_youtube",
                    "description": "Play YouTube video/music",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Video/song"}
                        },
                        "required": ["query"]
                    },
                    "function": web_ops.play
                },
                {
                    "name": "open_website",
                    "description": "Open website",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "Website URL"}
                        },
                        "required": ["url"]
                    },
                    "function": web_ops.open_website
                },
                {
                    "name": "wikipedia_search",
                    "description": "Search Wikipedia",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    },
                    "function": web_ops.wikipedia
                },
                {
                    "name": "get_weather",
                    "description": "Get weather",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": web_ops.weather
                },
            ],
            
            # ═══════════════════════════════════════════════════════════
            # FILES - Load when: file, folder, create, delete, search
            # ═══════════════════════════════════════════════════════════
            "files": [
                {
                    "name": "create_file",
                    "description": "Create file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"}
                        },
                        "required": ["path"]
                    },
                    "function": file_ops.create_file
                },
                {
                    "name": "create_folder",
                    "description": "Create folder",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Folder path"}
                        },
                        "required": ["path"]
                    },
                    "function": file_ops.create_folder
                },
                {
                    "name": "delete_file",
                    "description": "Delete file/folder",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path"}
                        },
                        "required": ["path"]
                    },
                    "function": file_ops.delete
                },
                {
                    "name": "search_files",
                    "description": "Search files",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "Directory"},
                            "filename": {"type": "string", "description": "Filename"}
                        },
                        "required": ["directory", "filename"]
                    },
                    "function": file_ops.search_by_name
                },
                {
                    "name": "organize_files",
                    "description": "Organize files by type",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "Directory"}
                        },
                        "required": ["directory"]
                    },
                    "function": file_ops.organize_by_type
                },
            ],
            
            # ═══════════════════════════════════════════════════════════
            # WINDOW - Load when: window, minimize, maximize, close
            # ═══════════════════════════════════════════════════════════
            "window": [
                {
                    "name": "minimize_window",
                    "description": """Minimize a window.
                    ENGLISH: 'minimize chrome', 'minimize this window', 'minimize notepad'
                    HINGLISH: 'chrome minimize karo', 'window minimize karo'
                    
                    If no title given, minimizes the active window.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Window title to minimize (e.g., 'Chrome', 'Notepad', 'VS Code'). Leave empty for active window."
                            }
                        },
                        "required": []
                    },
                    "function": window_ops.minimize
                },
                {
                    "name": "maximize_window",
                    "description": """Maximize a window.
                    ENGLISH: 'maximize chrome', 'maximize this window', 'maximize notepad', 'make chrome fullscreen'
                    HINGLISH: 'chrome maximize karo', 'chrome bada karo', 'window maximize karo'
                    
                    If no title given, maximizes the active window.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Window title to maximize (e.g., 'Chrome', 'Notepad', 'VS Code'). Leave empty for active window."
                            }
                        },
                        "required": []
                    },
                    "function": window_ops.maximize
                },
                {
                    "name": "close_window",
                    "description": """Close a window.
                    ENGLISH: 'close chrome', 'close this window', 'close notepad'
                    HINGLISH: 'chrome band karo', 'window close karo'
                    
                    If no title given, closes the active window.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Window title to close (e.g., 'Chrome', 'Notepad', 'VS Code'). Leave empty for active window."
                            }
                        },
                        "required": []
                    },
                    "function": window_ops.close
                },
                {
                    "name": "activate_window",
                    "description": """Bring a window to foreground.
                    ENGLISH: 'focus chrome', 'switch to notepad', 'bring chrome to front'
                    HINGLISH: 'chrome pe jao', 'notepad open karo'""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Window title to activate"
                            }
                        },
                        "required": ["title"]
                    },
                    "function": window_ops.activate
                },
                {
                    "name": "list_all_windows",
                    "description": """List all open windows.
                    ENGLISH: 'list windows', 'show all windows', 'what windows are open'
                    HINGLISH: 'sare windows dikhao', 'konse windows khule hain'""",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": window_ops.list_windows
                },
            ],

            # ═══════════════════════════════════════════════════════════
            # KEYBOARD - Load when: copy, paste, undo, save, tab, key
            # ═══════════════════════════════════════════════════════════
            "keyboard": [
                {
                    "name": "press_key",
                    "description": "Press a single keyboard key. Use when user says 'press enter', 'press escape', 'press f5', 'dabao space', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Key name: enter, escape, space, tab, f5, f12, backspace, delete"}
                        },
                        "required": ["key"]
                    },
                    "function": keyboard_ops.press
                },
                {
                    "name": "copy_shortcut",
                    "description": "Copy selected text to clipboard using Ctrl+C. Use ONLY when user says 'copy', 'copy this', 'copy karo', 'clipboard me copy'. Do NOT use for typing the word 'copy'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.copy
                },
                {
                    "name": "paste_shortcut",
                    "description": "Paste clipboard content using Ctrl+V. Use when user says 'paste', 'paste karo', 'paste here', 'yaha paste karo'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.paste
                },
                {
                    "name": "cut_shortcut",
                    "description": "Cut selected text using Ctrl+X. Use when user says 'cut', 'cut this', 'cut karo'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.cut
                },
                {
                    "name": "undo_action",
                    "description": "Undo last action using Ctrl+Z. Use when user says 'undo', 'undo karo', 'undo that', 'reverse last action'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.undo
                },
                {
                    "name": "redo_action",
                    "description": "Redo last undone action using Ctrl+Y. Use when user says 'redo', 'redo karo', 'redo that'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.redo
                },
                {
                    "name": "select_all_text",
                    "description": "Select all text using Ctrl+A. Use when user says 'select all', 'select everything', 'sab select karo'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.select_all
                },
                {
                    "name": "save_file",
                    "description": "Save current file using Ctrl+S. Use when user says 'save', 'save file', 'save this', 'file save karo'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.save
                },
                {
                    "name": "find_text",
                    "description": "Open find/search dialog using Ctrl+F. Use when user says 'find', 'search', 'find text', 'ctrl f'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.find
                },
                {
                    "name": "open_new_tab",
                    "description": "Open new browser tab using Ctrl+T. Use when user says 'new tab', 'open tab', 'naya tab'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.new_tab
                },
                {
                    "name": "close_current_tab",
                    "description": "Close current browser tab using Ctrl+W. Use when user says 'close tab', 'tab band karo'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.close_tab
                },
                {
                    "name": "refresh_page",
                    "description": "Refresh current page using F5. Use when user says 'refresh', 'reload', 'refresh page', 'page refresh karo'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.refresh
                },
                {
                    "name": "press_escape",
                    "description": "Press Escape key. Use when user says 'escape', 'press escape', 'cancel'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": keyboard_ops.escape
                },
                {
                    "name": "press_enter",
                    "description": "Press Enter key one or multiple times. Use when user says 'press enter', 'enter dabao', 'hit enter'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "times": {"type": "integer", "description": "Number of times to press (default 1)", "default": 1}
                        },
                        "required": []
                    },
                    "function": keyboard_ops.enter
                },
            ],

            # ═══════════════════════════════════════════════════════════
            # MEDIA - Load when: play, pause, next, previous, stop
            # ═══════════════════════════════════════════════════════════
            "media": [
                {
                    "name": "play_pause_media",
                    "description": "Toggle play/pause for currently playing media (music, video). Use when user says 'play', 'pause', 'play karo', 'pause karo', 'music chala', 'rok do'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": media_ops.play_pause
                },
                {
                    "name": "next_track",
                    "description": "Skip to next track/song. Use when user says 'next song', 'next track', 'skip', 'agla gaana', 'next bajao'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": media_ops.next_track
                },
                {
                    "name": "previous_track",
                    "description": "Go to previous track/song. Use when user says 'previous song', 'previous track', 'go back', 'pichla gaana', 'back'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": media_ops.previous_track
                },
                {
                    "name": "stop_media",
                    "description": "Stop media playback completely. Use when user says 'stop music', 'stop playing', 'band karo', 'stop'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": media_ops.stop
                },
            ],


            # ═══════════════════════════════════════════════════════════
            # REMINDER - Load when: remind, reminder, timer, alarm
            # ═══════════════════════════════════════════════════════════
            "reminder": [
                {
                    "name": "remind_in",
                    "description": "Set reminder X minutes from now. Use when user says 'remind me in 10 minutes', 'reminder 5 minute mein', '30 minutes baad yaad dilao'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "What to remind about"},
                            "minutes": {"type": "integer", "description": "Minutes from now"},
                            "description": {"type": "string", "description": "Optional details", "default": ""}
                        },
                        "required": ["title", "minutes"]
                    },
                    "function": reminder_ops.remind_in
                },
                {
                    "name": "remind_at",
                    "description": "Set reminder at specific time. Use when user says 'remind me at 5 PM', '3 baje yaad dilao', 'reminder at 10:30'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "What to remind about"},
                            "hour": {"type": "integer", "description": "Hour (0-23)"},
                            "minute": {"type": "integer", "description": "Minute (0-59)", "default": 0},
                            "description": {"type": "string", "description": "Optional details", "default": ""}
                        },
                        "required": ["title", "hour"]
                    },
                    "function": reminder_ops.remind_at
                },
                {
                    "name": "get_reminders",
                    "description": "Show all active reminders. Use when user says 'show my reminders', 'list reminders', 'mere reminders dikhao'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": reminder_ops.get_reminders
                },
                {
                    "name": "set_timer",
                    "description": "Start countdown timer. Alias for start_timer. Use when user says 'set timer', 'set 30 second timer'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "seconds": {"type": "integer", "description": "Duration in seconds"},
                            "name": {"type": "string", "description": "Timer name", "default": "Timer"}
                        },
                        "required": ["seconds"]
                    },
                    "function": reminder_ops.set_timer
                },
                {
                    "name": "stop_timer",
                    "description": "Stop active timer. Use when user says 'stop timer', 'cancel timer', 'timer band karo'.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": reminder_ops.stop_timer
                },
            ],

                        # ═══════════════════════════════════════════════════════════
            # WHATSAPP - Load when: whatsapp, wa, message, bhej, bhejo
            # ═══════════════════════════════════════════════════════════
            "whatsapp": [
                {
                    "name": "send_whatsapp",
                    "description": """Send WhatsApp message to someone. ALWAYS use this when user wants to SEND/MESSAGE someone.
                    
                    ⚠️ IMPORTANT: DO NOT use 'save_whatsapp_contact' for sending messages. This function is for SENDING.
                    
                    ═══════════════════════════════════════════════════════════════
                    ENGLISH PATTERNS:
                    ═══════════════════════════════════════════════════════════════
                    • 'send whatsapp to john saying hello'
                    • 'message john on whatsapp'
                    • 'whatsapp mom saying I'll be late'
                    • 'text dad on whatsapp hello'
                    • 'send hello to john on whatsapp'
                    
                    ═══════════════════════════════════════════════════════════════
                    HINGLISH PATTERNS (Hindi + English):
                    ═══════════════════════════════════════════════════════════════
                    • 'john ko whatsapp bhejo' → send to john
                    • 'mummy ko message karo' → message mom
                    • 'papa ko bhej do meeting at 5' → send to dad
                    • 'abhay ko whatsapp bhejo hi bolo' → send "hi" to abhay
                    • 'bhai ko msg kar hello' → message brother
                    • 'dost ko whatsapp pe bolo kal milte' → tell friend on whatsapp
                    
                    ═══════════════════════════════════════════════════════════════
                    KEY DETECTION WORDS:
                    ═══════════════════════════════════════════════════════════════
                    • 'bhejo' / 'bhej' / 'bhej do' = SEND (use send_whatsapp)
                    • 'bolo' / 'bol do' = SAY/TELL (use send_whatsapp)
                    • 'message karo' / 'msg kar' = MESSAGE (use send_whatsapp)
                    • 'ko whatsapp' = TO someone on whatsapp (use send_whatsapp)
                    
                    ═══════════════════════════════════════════════════════════════
                    SMART FEATURES:
                    ═══════════════════════════════════════════════════════════════
                    • Contact exists → sends directly
                    • Contact unknown → asks for phone number
                    • Message missing → asks what to send
                    • Phone number given → saves contact automatically""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": "Name (john, mummy, papa, bhai, dost) or phone number (9876543210). Extract from 'X ko' pattern."
                            },
                            "message": {
                                "type": "string",
                                "description": "Message text. Extract from 'saying X', 'bolo X', 'X bhej do'. Example: hello, hi, meeting at 5"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number for new contact (optional, rarely needed)"
                            }
                        },
                        "required": ["recipient"]
                    },
                    "function": whatsapp_ops.send_whatsapp
                },
                {
                    "name": "save_whatsapp_contact",
                    "description": """Save WhatsApp contact to database. ONLY use when user explicitly wants to SAVE/ADD a contact.
                    
                    ⚠️ DO NOT use this for sending messages! Use 'send_whatsapp' for sending.
                    
                    USE THIS ONLY FOR:
                    • 'save john whatsapp number 9876543210'
                    • 'add whatsapp contact mom 9123456789'
                    • 'john ka number save karo 9876543210'
                    • 'mummy ka whatsapp number add karo'
                    
                    KEYWORDS: 'save', 'add', 'number save karo', 'contact add karo'""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Contact name to save"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number (10 digits)"
                            }
                        },
                        "required": ["name", "phone"]
                    },
                    "function": whatsapp_ops.save_whatsapp_contact
                },
                {
                    "name": "list_whatsapp_contacts",
                    "description": """Show all saved WhatsApp contacts.
                    ENGLISH: 'show my whatsapp contacts', 'list whatsapp numbers'
                    HINGLISH: 'mere whatsapp contacts dikhao', 'whatsapp ke contact list karo'""",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": whatsapp_ops.list_whatsapp_contacts
                },
                {
                    "name": "send_whatsapp_file",
                    "description": """Send file/image on WhatsApp. Opens file picker dialog.
                    ONLY use this when user explicitly says 'send file', 'share file', 'send image'.
                    DO NOT use for sending text messages.
                    ENGLISH: 'send file to john on whatsapp', 'share image with mom'
                    HINGLISH: 'abhay ko file bhejo', 'mummy ko photo share karo'
                    
                    Note: If no file_path provided, automatically opens file picker dialog.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": "Name or phone number"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Optional: Full path to file. Leave empty to open picker."
                            },
                            "caption": {
                                "type": "string",
                                "description": "Optional: Caption/message with file"
                            }
                        },
                        "required": ["recipient"]
                    },
                    "function": whatsapp_ops.send_whatsapp_file
                },
                {
                    "name": "schedule_whatsapp",
                    "description": """Schedule WhatsApp message for later.
                    ENGLISH: 'schedule whatsapp to john at 5 PM saying meeting reminder'
                    HINGLISH: 'john ko 5 baje whatsapp bhejo meeting reminder'""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {"type": "string", "description": "Name or phone"},
                            "message": {"type": "string", "description": "Message text"},
                            "hour": {"type": "integer", "description": "Hour (0-23)"},
                            "minute": {"type": "integer", "description": "Minute (0-59)", "default": 0}
                        },
                        "required": ["recipient", "message", "hour"]
                    },
                    "function": whatsapp_ops.schedule_whatsapp
                },
            ],

                        # ═══════════════════════════════════════════════════════════
            # EMAIL - Load when: email, mail, send email
            # ═══════════════════════════════════════════════════════════
            "email": [
                {
                    "name": "send_email",
                    "description": """Send email to contact or email address.
                    ENGLISH: 'send email to john with subject hello', 'email mom saying happy birthday'
                    HINGLISH: 'john ko email bhejo', 'mummy ko mail karo', 'boss ko email bhej do'
                    
                    Smart features:
                    - If contact exists: sends directly
                    - If contact unknown: asks for email address
                    - If subject/body missing: asks for it""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {"type": "string", "description": "Name or email address"},
                            "subject": {"type": "string", "description": "Email subject line"},
                            "body": {"type": "string", "description": "Email body/message content"},
                            "email": {"type": "string", "description": "Email address (optional, for new contacts)"}
                        },
                        "required": ["recipient"]
                    },
                    "function": email_ops.send_email
                },
                {
                    "name": "save_email_contact",
                    "description": """Save email contact.
                    ENGLISH: 'save john email john@gmail.com', 'add email contact'
                    HINGLISH: 'john ka email save karo'""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Contact name"},
                            "email": {"type": "string", "description": "Email address"}
                        },
                        "required": ["name", "email"]
                    },
                    "function": email_ops.save_email_contact
                },
                {
                    "name": "list_email_contacts",
                    "description": """Show all email contacts.
                    ENGLISH: 'show my email contacts', 'list email addresses'
                    HINGLISH: 'email contacts dikhao'""",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": email_ops.list_email_contacts
                },
                {
                    "name": "check_email_config",
                    "description": """Check if email is configured properly.
                    Use when: 'is email configured', 'check email setup', 'email settings'""",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": email_ops.check_email_config
                },
            ],
                        # ═══════════════════════════════════════════════════════════
            # SENTRY - Load when: sentry, surveillance, guard, nazar, raksha
            # ═══════════════════════════════════════════════════════════
            "sentry": [
                {
                    "name": "start_sentry",
                    "description": """Start sentry mode - motion detection surveillance with Telegram alerts.
                    
                    ENGLISH COMMANDS:
                    • 'start sentry'
                    • 'activate sentry for 60 minutes'
                    • 'turn on surveillance'
                    • 'enable motion detection'
                    • 'start security camera'
                    
                    HINGLISH COMMANDS:
                    • 'sentry chalu karo'
                    • 'sentry mode on karo'
                    • 'surveillance shuru karo'
                    • 'camera se nazar rakho'
                    • 'motion detect karo 30 minute ke liye'
                    • 'security mode activate karo'
                    • 'raksha mode on karo'
                    
                    FEATURES:
                    • Webcam-based motion detection
                    • Telegram photo alerts on movement
                    • Auto-breaks every 20 min (5 min rest)
                    • Max 120 minutes runtime
                    • Self-destructs alert photos after sending
                    
                    IMPORTANT: Requires Telegram bot token and chat ID in .env""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "duration_min": {
                                "type": "integer",
                                "description": "Duration in minutes (1-120). Default 60. Examples: 30, 60, 90",
                                "default": 60
                            }
                        },
                        "required": []
                    },
                    "function": sentry_mode.start_sentry
                },
                {
                    "name": "stop_sentry",
                    "description": """Stop active sentry mode immediately.
                    
                    ENGLISH: 'stop sentry', 'turn off surveillance', 'deactivate sentry', 'stop security'
                    HINGLISH: 'sentry band karo', 'surveillance off karo', 'sentry rok do', 'camera band karo'""",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": sentry_mode.stop_sentry
                },
                {
                    "name": "sentry_status",
                    "description": """Check current sentry mode status and stats.
                    
                    ENGLISH: 'sentry status', 'is sentry active', 'check surveillance', 'sentry info'
                    HINGLISH: 'sentry ka status', 'sentry chal raha hai kya', 'sentry check karo', 'kitne alerts aaye'""",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                    "function": sentry_mode.sentry_status
                },
            ],


                        
        }
    
    def _get_core_functions(self):
        """Get core functions (always loaded)"""
        return self.all_functions["core"]
    
    def detect_category(self, user_input: str):
        """Detect which category to load based on user input"""
        text_lower = user_input.lower()

        if any(word in text_lower for word in [
            "whatsapp", "wa ", "watsapp",
            "bhejo", "bhej", "bhejdo", "bhej do",
            "message karo", "msg bhej",
            "whatsapp pe", "whatsapp par",
            "wa me", "wa mein"
        ]):
            return "whatsapp"

        # Add after whatsapp detection
        if any(word in text_lower for word in [
            "email", "mail", "gmail", "send mail",
            "email bhejo", "mail karo", "email bhej"
        ]):
            return "email"

        if any(word in text_lower for word in ["remind me", "reminder", "timer", "yaad dilao", "alarm", "set reminder", "start timer"]):
            return "reminder"
        
        # Check for keywords
        if any(word in text_lower for word in ["lock", "shutdown", "restart", "sleep", "brightness", "system info"]):
            return "system"
        
        if any(word in text_lower for word in ["search", "google", "youtube", "play", "wikipedia", "weather", "website"]):
            return "web"
        
        if any(word in text_lower for word in ["file", "folder", "create", "delete", "organize", "search file"]):
            return "files"
        
        if any(word in text_lower for word in ["window", "minimize", "maximize"]):
            return "window"

        if any(word in text_lower for word in ["copy", "paste", "cut", "undo", "redo", "select all", "save", "find", "new tab", "close tab", "refresh", "press", "hotkey", "escape", "enter"]):
            return "keyboard"
        
        if any(word in text_lower for word in ["play", "pause", "next", "previous", "skip", "stop music", "stop playing", "next song", "previous song", "next track", "gaana", "bajao"]):
            return "media"

                # Sentry mode detection
        if any(word in text_lower for word in [
            "sentry", "surveillance", "security", "guard", "nazar", "raksha",
            "motion detect", "camera", "webcam", "monitor",
            "sentry mode", "sentry chalu", "sentry band", "sentry status",
            "camera se dekho", "motion check", "security mode",
            "surveillance on", "surveillance off", "nazar rakho"
        ]):
            return "sentry"
        
        return None  # Only core functions
    
    def get_functions_for_input(self, user_input: str):
        """Get relevant functions based on input"""
        functions = self._get_core_functions().copy()  # Always include core
        
        category = self.detect_category(user_input)
        if category:
            functions.extend(self.all_functions[category])
        
        return functions
    
    def get_groq_schema(self, user_input: str = ""):
        """Get Groq schema (smart loading)"""
        functions = self.get_functions_for_input(user_input) if user_input else self._get_core_functions()
        
        return [
            {
                "name": func["name"],
                "description": func["description"],
                "parameters": func["parameters"]
            }
            for func in functions
        ]
    
    def get_function(self, name: str):
        """Get function by name"""
        for category_funcs in self.all_functions.values():
            for func in category_funcs:
                if func["name"] == name:
                    return func["function"]
        return None
    
    def execute(self, func_name: str, **kwargs):
        """Execute function by name"""
        func = self.get_function(func_name)
        if func:
            return func(**kwargs)
        return {"status": "error", "message": f"Function '{func_name}' not found"}
    
    def get_function_count(self):
        """Total functions"""
        total = sum(len(funcs) for funcs in self.all_functions.values())
        return total


# Global instance
registry = FunctionRegistry()