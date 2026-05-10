"""
Function Registry - Smart grouped loading for performance
"""

from src.automation import system_ops, utility_ops, keyboard_ops, window_ops, file_ops, web_ops, media_ops, reminder_ops, email_ops
from src.automation import whatsapp as whatsapp_ops
from src.automation import sentry_mode
from src.automation import vision_ops


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
                    "description": "Type a literal string of text using the keyboard. DO NOT use this for keyboard shortcuts (like 'ctrl+c' or 'enter') - use execute_keyboard_shortcut instead.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The exact text to type out."}
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
                    "name": "control_volume",
                    "description": "Control system volume. Use for volume up, down, or mute.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "'up', 'down', or 'mute'"},
                            "steps": {"type": "integer", "description": "Number of steps (default 5)", "default": 5}
                        },
                        "required": ["action"]
                    },
                    "function": system_ops.control_volume
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
                {
                    "name": "analyze_screen",
                    "description": "Take a silent screenshot and analyze what is currently visible on the user's screen. Use this when the user asks questions requiring visual context, like: 'look at this', 'what's on my screen', 'read this code', 'summarize this image'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The question or instruction about the screen. Example: 'Describe the errors in this code', 'Summarize this website'."}
                        },
                        "required": ["prompt"]
                    },
                    "function": vision_ops.analyze_screen
                },
            ],
            
            # ═══════════════════════════════════════════════════════════
            # SYSTEM - Load when user mentions: lock, shutdown, restart, sleep
            # ═══════════════════════════════════════════════════════════
            "system": [
                {
                    "name": "control_system",
                    "description": "Control system power and status. Use for lock, shutdown, restart, sleep, or getting system info.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string", 
                                "description": "Action: 'lock', 'shutdown', 'restart', 'sleep', 'cancel', or 'info'"
                            },
                            "delay": {
                                "type": "integer", 
                                "description": "Delay in seconds for shutdown/restart (default 0)",
                                "default": 0
                            }
                        },
                        "required": ["action"]
                    },
                    "function": system_ops.control_system
                },
                {
                    "name": "control_brightness",
                    "description": "Control screen brightness. Use for brightness up or down.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "'up' or 'down'"},
                            "steps": {"type": "integer", "description": "Number of steps (default 10)", "default": 10}
                        },
                        "required": ["action"]
                    },
                    "function": system_ops.control_brightness
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
                {
                    "name": "open_location",
                    "description": "Open a file or folder location in File Explorer. Use when user says 'show me the files', 'open folder', 'show folder', 'open location'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to file or directory"}
                        },
                        "required": ["path"]
                    },
                    "function": file_ops.open_location
                },
            ],
            
            # ═══════════════════════════════════════════════════════════
            # WINDOW - Load when: window, minimize, maximize, close
            # ═══════════════════════════════════════════════════════════
            "window": [
                {
                    "name": "manage_window",
                    "description": "Manage application windows (minimize, maximize, close, activate/focus, or list).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Action: 'minimize', 'maximize', 'close', 'activate', or 'list'"
                            },
                            "title": {
                                "type": "string",
                                "description": "Window title (e.g. 'Chrome', 'Notepad'). Leave empty for active window unless action is 'activate'."
                            }
                        },
                        "required": ["action"]
                    },
                    "function": window_ops.manage_window
                }
            ],

            # ═══════════════════════════════════════════════════════════
            # KEYBOARD - Load when: copy, paste, undo, save, tab, key
            # ═══════════════════════════════════════════════════════════
            "keyboard": [
                {
                    "name": "execute_keyboard_shortcut",
                    "description": "Execute a single key or a combination of keys (e.g. 'ctrl+c', 'enter', 'f5', 'ctrl+v', 'select all'). Use this for copy, paste, cut, undo, refresh, hitting enter, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keys": {
                                "type": "string", 
                                "description": "The exact shortcut to press. Examples: 'ctrl+c', 'ctrl+v', 'ctrl+a', 'enter', 'escape', 'tab', 'backspace'"
                            }
                        },
                        "required": ["keys"]
                    },
                    "function": keyboard_ops.execute_shortcut
                }
            ],

            # ═══════════════════════════════════════════════════════════
            # MEDIA - Load when: play, pause, next, previous, stop
            # ═══════════════════════════════════════════════════════════
            "media": [
                {
                    "name": "control_media",
                    "description": "Control media playback (music, video). Use for play, pause, next, previous, or stop.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The action to perform: 'play', 'pause', 'next', 'previous', or 'stop'"
                            }
                        },
                        "required": ["action"]
                    },
                    "function": media_ops.control_media
                }
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
        
        if any(word in text_lower for word in ["search", "google", "youtube", "play", "wikipedia", "weather", "website", "news", "who is", "what is", "tell me about", "find out"]):
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
    
    # ------------------------------------------------------------------
    # Thread-safe confirmation dispatcher
    # The GUI registers a callable here at startup so dangerous-action
    # dialogs are always shown on the main thread, preventing deadlocks.
    # Signature: dispatcher(title: str, text: str) -> bool
    # ------------------------------------------------------------------
    _confirm_dispatcher = None

    @classmethod
    def register_confirm_dispatcher(cls, dispatcher):
        """Register a thread-safe confirmation callback (called once by the GUI)."""
        cls._confirm_dispatcher = dispatcher

    def _confirm_dangerous_action(self, func_name: str, kwargs: dict) -> bool:
        """
        Ask the user whether to allow a dangerous action.
        Always runs the dialog on the main thread to avoid Win32 deadlocks.
        """
        import sys
        title = f"Security Confirmation: {func_name}"
        text = (
            f"IntelliDesk AI wants to execute a DESTRUCTIVE action:\n\n"
            f"  Action: {func_name}\n"
            f"  Arguments: {kwargs}\n\n"
            f"Allow this?"
        )

        # Prefer the registered GUI dispatcher (guaranteed main-thread)
        if self._confirm_dispatcher is not None:
            return self._confirm_dispatcher(title, text)

        # Fallback: use MessageBoxW but only when we are already on the main
        # thread (safe), otherwise fall back to a console prompt.
        if sys.platform == "win32":
            import threading
            import ctypes
            if threading.current_thread() is threading.main_thread():
                result = ctypes.windll.user32.MessageBoxW(0, text, title, 0x40034)
                return result == 6  # IDYES
            else:
                # Background thread — use a console prompt instead to avoid deadlock
                import logging
                logging.getLogger("FunctionRegistry").warning(
                    "MessageBoxW skipped (background thread) — falling back to console confirm."
                )
                answer = input(f"\n⚠️  DANGEROUS ACTION: {func_name} {kwargs}\n  Type YES to allow: ").strip()
                return answer.upper() == "YES"

        # Non-Windows fallback
        answer = input(f"\n⚠️  DANGEROUS ACTION: {func_name} {kwargs}\n  Type YES to allow: ").strip()
        return answer.upper() == "YES"

    def get_function(self, name: str):
        """Get function by name"""
        for category_funcs in self.all_functions.values():
            for func in category_funcs:
                if func["name"] == name:
                    return func["function"]
        return None

    def execute(self, func_name: str, **kwargs):
        """Execute function by name with thread-safe dangerous-action guard."""
        DANGEROUS_FUNCTIONS = {"shutdown_system", "restart_system", "sleep_system", "delete_file"}

        if func_name in DANGEROUS_FUNCTIONS:
            allowed = self._confirm_dangerous_action(func_name, kwargs)
            if not allowed:
                return {
                    "status": "error",
                    "message": "User denied the execution of this action for safety reasons."
                }

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