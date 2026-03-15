"""
═══════════════════════════════════════════════════════════════════════════════
INTELLIDESK AI - AUTOMATION EXECUTOR
═══════════════════════════════════════════════════════════════════════════════
Connects Intent Parser to Automation Modules
Routes 97+ intents to their respective handlers
═══════════════════════════════════════════════════════════════════════════════
"""

from src.utils.logger import Logger
from src.database.db_manager import DatabaseManager

# Import all automation modules
from src.automation import whatsapp
from src.automation import email_ops
from src.automation import system_ops
from src.automation import file_ops
from src.automation import web_ops
from src.automation import utility_ops
from src.automation import media_ops
from src.automation import reminder_ops
from src.automation import keyboard_ops
from src.automation import window_ops
from src.automation import network_ops

logger = Logger.get_logger("Executor")


class AutomationExecutor:
    """
    Routes intents to automation modules and executes them
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        
        # Map intents to handler functions
        self.handlers = {
            # ═══════════════════════════════════════════════════════════
            # WHATSAPP
            # ═══════════════════════════════════════════════════════════
            "whatsapp": self._handle_whatsapp,
            
            # ═══════════════════════════════════════════════════════════
            # EMAIL
            # ═══════════════════════════════════════════════════════════
            "email": self._handle_email,
            
            # ═══════════════════════════════════════════════════════════
            # SYSTEM OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "screenshot": self._handle_screenshot,
            "system_shutdown": self._handle_shutdown,
            "system_restart": self._handle_restart,
            "system_lock": self._handle_lock,
            "system_sleep": self._handle_sleep,
            "system_info": self._handle_system_info,
            "volume_up": self._handle_volume_up,
            "volume_down": self._handle_volume_down,
            "volume_mute": self._handle_volume_mute,
            "brightness_up": self._handle_brightness_up,
            "brightness_down": self._handle_brightness_down,
            "app_open": self._handle_app_open,
            "app_close": self._handle_app_close,
            
            # ═══════════════════════════════════════════════════════════
            # FILE OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "file_create": self._handle_file_create,
            "file_delete": self._handle_file_delete,
            "file_rename": self._handle_file_rename,
            "file_move": self._handle_file_move,
            "file_copy": self._handle_file_copy,
            "file_search": self._handle_file_search,
            "file_organize": self._handle_file_organize,
            "file_info": self._handle_file_info,
            
            # ═══════════════════════════════════════════════════════════
            # WEB OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "web_search": self._handle_web_search,
            "youtube_search": self._handle_youtube_search,
            "youtube_play": self._handle_youtube_play,
            "web_open": self._handle_web_open,
            "wikipedia": self._handle_wikipedia,
            "weather": self._handle_weather,
            "download": self._handle_download,
            
            # ═══════════════════════════════════════════════════════════
            # UTILITY OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "time": self._handle_time,
            "date": self._handle_date,
            "calculate": self._handle_calculate,
            "generate_password": self._handle_generate_password,
            "text_to_speech": self._handle_text_to_speech,
            "note_create": self._handle_note_create,
            "note_list": self._handle_note_list,
            "note_delete": self._handle_note_delete,
            "random_number": self._handle_random_number,
            "flip_coin": self._handle_flip_coin,
            "roll_dice": self._handle_roll_dice,
            
            # ═══════════════════════════════════════════════════════════
            # MEDIA OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "media_play_pause": self._handle_media_play_pause,
            "media_next": self._handle_media_next,
            "media_previous": self._handle_media_previous,
            "media_stop": self._handle_media_stop,
            
            # ═══════════════════════════════════════════════════════════
            # REMINDER OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "reminder_create": self._handle_reminder_create,
            "reminder_list": self._handle_reminder_list,
            "timer_start": self._handle_timer_start,
            "timer_stop": self._handle_timer_stop,
            
            # ═══════════════════════════════════════════════════════════
            # KEYBOARD OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "keyboard_type": self._handle_keyboard_type,
            "keyboard_copy": self._handle_keyboard_copy,
            "keyboard_paste": self._handle_keyboard_paste,
            "keyboard_cut": self._handle_keyboard_cut,
            "keyboard_undo": self._handle_keyboard_undo,
            "keyboard_redo": self._handle_keyboard_redo,
            "keyboard_select_all": self._handle_keyboard_select_all,
            "keyboard_save": self._handle_keyboard_save,
            "keyboard_find": self._handle_keyboard_find,
            "keyboard_enter": self._handle_keyboard_enter,
            
            # ═══════════════════════════════════════════════════════════
            # WINDOW OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "window_minimize": self._handle_window_minimize,
            "window_maximize": self._handle_window_maximize,
            "window_close": self._handle_window_close,
            "window_list": self._handle_window_list,
            "window_switch": self._handle_window_switch,
            
            # ═══════════════════════════════════════════════════════════
            # NETWORK OPERATIONS
            # ═══════════════════════════════════════════════════════════
            "network_check": self._handle_network_check,
            "network_ip_local": self._handle_network_ip_local,
            "network_ip_public": self._handle_network_ip_public,
            "network_ping": self._handle_network_ping,
            "network_dns": self._handle_network_dns,
            "network_info": self._handle_network_info,
            
            # ═══════════════════════════════════════════════════════════
            # CLIPBOARD
            # ═══════════════════════════════════════════════════════════
            "clipboard_copy_text": self._handle_clipboard_copy,
            "clipboard_get": self._handle_clipboard_get,
            
            # ═══════════════════════════════════════════════════════════
            # CODE GENERATION & EXPLAIN
            # ═══════════════════════════════════════════════════════════
            "code_generate": self._handle_code_generate,
            "explain": self._handle_explain,
            "chat": self._handle_chat,
        }
    
    def execute(self, intent_data):
        """
        Execute automation based on intent
        
        Args:
            intent_data: Dict from IntentParser
                {
                    "intent": "whatsapp",
                    "params": {"recipient": "mom", "message": "hello"},
                    "confidence": 0.95,
                    ...
                }
        
        Returns:
            Dict: {"status": "success/error", "message": "...", "data": {...}}
        """
        intent = intent_data.get("intent", "")
        params = intent_data.get("params", {})
        original = intent_data.get("original", "")
        
        logger.info(f"Executing: {intent} | Params: {params}")
        
        # Save task to database
        task_id = self.db.save_task(
            task_type=intent,
            command=original,
            status="processing"
        )
        
        # Get handler
        handler = self.handlers.get(intent)
        
        if not handler:
            error_msg = f"No handler for intent: {intent}"
            logger.warning(error_msg)
            
            if task_id:
                self.db.update_task(task_id, "failed", error=error_msg)
            
            return {
                "status": "error",
                "message": f"I don't know how to handle: {intent}",
                "intent": intent
            }
        
        # Execute
        try:
            result = handler(params)
            
            # Update task
            if task_id:
                if result.get("status") == "success":
                    self.db.update_task(task_id, "completed", result=result.get("message"))
                elif result.get("status") == "needs_info":
                    self.db.update_task(task_id, "pending", result=result.get("message"))
                else:
                    self.db.update_task(task_id, "failed", error=result.get("message"))
            
            return result
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            logger.error(error_msg)
            
            if task_id:
                self.db.update_task(task_id, "failed", error=error_msg)
            
            return {
                "status": "error",
                "message": error_msg
            }
    
    # ═══════════════════════════════════════════════════════════════════════
    # WHATSAPP HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_whatsapp(self, params):
        recipient = params.get("recipient")
        message = params.get("message")
        
        if not recipient:
            return {"status": "needs_info", "message": "Kisko message bhejun? (Name ya number batao)"}
        
        if not message:
            return {"status": "needs_info", "message": "Kya message bhejun?"}
        
        result = whatsapp.send(recipient, message)
        
        # Handle needs_number case
        if result.get("status") == "needs_number":
            return {
                "status": "needs_info",
                "message": result.get("message"),
                "data": result.get("data")
            }
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════════
    # EMAIL HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_email(self, params):
        to = params.get("to")
        subject = params.get("subject", "")
        body = params.get("body", "")
        
        if not to:
            return {"status": "needs_info", "message": "Email kis ko bhejun?"}
        
        if not subject:
            return {"status": "needs_info", "message": "Email ka subject kya rakhu?"}
        
        if not body:
            body = subject  # Use subject as body if not provided
        
        return email_ops.send(to, subject, body)
    
    # ═══════════════════════════════════════════════════════════════════════
    # SYSTEM HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_screenshot(self, params):
        filename = params.get("filename")
        return system_ops.screenshot(filename)
    
    def _handle_shutdown(self, params):
        return system_ops.shutdown()
    
    def _handle_restart(self, params):
        return system_ops.restart()
    
    def _handle_lock(self, params):
        return system_ops.lock()
    
    def _handle_sleep(self, params):
        return system_ops.sleep()
    
    def _handle_system_info(self, params):
        return system_ops.system_info()
    
    def _handle_volume_up(self, params):
        return system_ops.volume_up()
    
    def _handle_volume_down(self, params):
        return system_ops.volume_down()
    
    def _handle_volume_mute(self, params):
        return system_ops.mute()
    
    def _handle_brightness_up(self, params):
        return system_ops.brightness_up()
    
    def _handle_brightness_down(self, params):
        return system_ops.brightness_down()
    
    def _handle_app_open(self, params):
        app = params.get("app")
        if not app:
            return {"status": "needs_info", "message": "Konsi app kholun?"}
        return system_ops.open_app(app)
    
    def _handle_app_close(self, params):
        app = params.get("app")
        if not app:
            return {"status": "needs_info", "message": "Konsi app band karun?"}
        return system_ops.close_app(app)
    
    # ═══════════════════════════════════════════════════════════════════════
    # FILE HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_file_create(self, params):
        name = params.get("name")
        if not name:
            return {"status": "needs_info", "message": "File/folder ka naam kya rakhu?"}
        
        # Determine if file or folder
        if "." in name:
            return file_ops.create_file(name)
        else:
            return file_ops.create_folder(name)
    
    def _handle_file_delete(self, params):
        name = params.get("name")
        if not name:
            return {"status": "needs_info", "message": "Konsi file/folder delete karun?"}
        return file_ops.delete(name)
    
    def _handle_file_rename(self, params):
        old_name = params.get("old_name")
        new_name = params.get("new_name")
        
        if not old_name or not new_name:
            return {"status": "needs_info", "message": "Purana naam aur naya naam dono batao"}
        
        return file_ops.rename(old_name, new_name)
    
    def _handle_file_move(self, params):
        source = params.get("source")
        destination = params.get("destination")
        
        if not source or not destination:
            return {"status": "needs_info", "message": "Source aur destination dono batao"}
        
        return file_ops.move(source, destination)
    
    def _handle_file_copy(self, params):
        source = params.get("source")
        destination = params.get("destination")
        
        if not source or not destination:
            return {"status": "needs_info", "message": "Source aur destination dono batao"}
        
        return file_ops.copy(source, destination)
    
    def _handle_file_search(self, params):
        filename = params.get("filename")
        if not filename:
            return {"status": "needs_info", "message": "Konsi file dhundhni hai?"}
        
        # Search in common locations
        import os
        search_paths = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
        ]
        
        for path in search_paths:
            result = file_ops.search_by_name(path, filename)
            if result.get("count", 0) > 0:
                return result
        
        return {"status": "success", "message": f"'{filename}' nahi mili", "results": [], "count": 0}
    
    def _handle_file_organize(self, params):
        folder = params.get("folder", "downloads")
        
        import os
        folder_paths = {
            "downloads": os.path.expanduser("~\\Downloads"),
            "desktop": os.path.expanduser("~\\Desktop"),
            "documents": os.path.expanduser("~\\Documents"),
            "pictures": os.path.expanduser("~\\Pictures"),
            "videos": os.path.expanduser("~\\Videos"),
            "music": os.path.expanduser("~\\Music"),
        }
        
        path = folder_paths.get(folder.lower(), folder)
        return file_ops.organize_by_type(path)
    
    def _handle_file_info(self, params):
        name = params.get("name")
        if not name:
            return {"status": "needs_info", "message": "Konsi file ki info chahiye?"}
        return file_ops.get_info(name)
    
    # ═══════════════════════════════════════════════════════════════════════
    # WEB HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_web_search(self, params):
        query = params.get("query")
        if not query:
            return {"status": "needs_info", "message": "Kya search karna hai?"}
        return web_ops.google(query)
    
    def _handle_youtube_search(self, params):
        query = params.get("query")
        if not query:
            return {"status": "needs_info", "message": "YouTube pe kya search karun?"}
        return web_ops.youtube(query)
    
    def _handle_youtube_play(self, params):
        query = params.get("query")
        if not query:
            return {"status": "needs_info", "message": "Kya play karun?"}
        return web_ops.play(query)
    
    def _handle_web_open(self, params):
        url = params.get("url")
        if not url:
            return {"status": "needs_info", "message": "Konsi website kholun?"}
        return web_ops.open_website(url)
    
    def _handle_wikipedia(self, params):
        query = params.get("query")
        if not query:
            return {"status": "needs_info", "message": "Wikipedia pe kya search karun?"}
        return web_ops.wikipedia(query)
    
    def _handle_weather(self, params):
        location = params.get("location", "")
        return web_ops.weather(location)
    
    def _handle_download(self, params):
        url = params.get("url")
        if not url:
            return {"status": "needs_info", "message": "Download URL batao"}
        return web_ops.download(url)
    
    # ═══════════════════════════════════════════════════════════════════════
    # UTILITY HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_time(self, params):
        return utility_ops.get_time()
    
    def _handle_date(self, params):
        return utility_ops.get_date()
    
    def _handle_calculate(self, params):
        expression = params.get("expression")
        if not expression:
            return {"status": "needs_info", "message": "Kya calculate karna hai?"}
        return utility_ops.calculate(expression)
    
    def _handle_generate_password(self, params):
        return utility_ops.generate_password()
    
    def _handle_text_to_speech(self, params):
        text = params.get("text")
        if not text:
            return {"status": "needs_info", "message": "Kya bolun?"}
        return utility_ops.speak(text)
    
    def _handle_note_create(self, params):
        content = params.get("content")
        if not content:
            return {"status": "needs_info", "message": "Note me kya likhu?"}
        return utility_ops.create_note(content)
    
    def _handle_note_list(self, params):
        return utility_ops.get_notes()
    
    def _handle_note_delete(self, params):
        note_id = params.get("note_id")
        if not note_id:
            return {"status": "needs_info", "message": "Konsa note delete karun? (ID batao)"}
        return utility_ops.delete_note(int(note_id))
    
    def _handle_random_number(self, params):
        min_val = int(params.get("min", 1))
        max_val = int(params.get("max", 100))
        return utility_ops.random_number(min_val, max_val)
    
    def _handle_flip_coin(self, params):
        return utility_ops.flip_coin()
    
    def _handle_roll_dice(self, params):
        return utility_ops.roll_dice()
    
    # ═══════════════════════════════════════════════════════════════════════
    # MEDIA HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_media_play_pause(self, params):
        return media_ops.play_pause()
    
    def _handle_media_next(self, params):
        return media_ops.next_track()
    
    def _handle_media_previous(self, params):
        return media_ops.previous_track()
    
    def _handle_media_stop(self, params):
        return media_ops.stop()
    
    # ═══════════════════════════════════════════════════════════════════════
    # REMINDER HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_reminder_create(self, params):
        task = params.get("task")
        minutes = params.get("minutes")
        
        if not task:
            return {"status": "needs_info", "message": "Kya yaad dilana hai?"}
        
        if not minutes:
            return {"status": "needs_info", "message": "Kitne minutes baad yaad dilau?"}
        
        return reminder_ops.remind_in(task, int(minutes))
    
    def _handle_reminder_list(self, params):
        return reminder_ops.get_reminders()
    
    def _handle_timer_start(self, params):
        seconds = params.get("seconds")
        if not seconds:
            return {"status": "needs_info", "message": "Kitne seconds ka timer?"}
        return reminder_ops.start_timer(int(seconds))
    
    def _handle_timer_stop(self, params):
        return reminder_ops.stop_timer()
    
    # ═══════════════════════════════════════════════════════════════════════
    # KEYBOARD HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_keyboard_type(self, params):
        text = params.get("text")
        if not text:
            return {"status": "needs_info", "message": "Kya type karun?"}
        return keyboard_ops.type_text(text)
    
    def _handle_keyboard_copy(self, params):
        return keyboard_ops.copy()
    
    def _handle_keyboard_paste(self, params):
        return keyboard_ops.paste()
    
    def _handle_keyboard_cut(self, params):
        return keyboard_ops.cut()
    
    def _handle_keyboard_undo(self, params):
        return keyboard_ops.undo()
    
    def _handle_keyboard_redo(self, params):
        return keyboard_ops.redo()
    
    def _handle_keyboard_select_all(self, params):
        return keyboard_ops.select_all()
    
    def _handle_keyboard_save(self, params):
        return keyboard_ops.save()
    
    def _handle_keyboard_find(self, params):
        return keyboard_ops.find()
    
    def _handle_keyboard_enter(self, params):
        return keyboard_ops.enter()
    
    # ═══════════════════════════════════════════════════════════════════════
    # WINDOW HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_window_minimize(self, params):
        title = params.get("title")
        return window_ops.minimize(title)
    
    def _handle_window_maximize(self, params):
        title = params.get("title")
        return window_ops.maximize(title)
    
    def _handle_window_close(self, params):
        title = params.get("title")
        return window_ops.close(title)
    
    def _handle_window_list(self, params):
        return window_ops.list_windows()
    
    def _handle_window_switch(self, params):
        return system_ops.switch_window()
    
    # ═══════════════════════════════════════════════════════════════════════
    # NETWORK HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_network_check(self, params):
        return network_ops.check_internet()
    
    def _handle_network_ip_local(self, params):
        return network_ops.local_ip()
    
    def _handle_network_ip_public(self, params):
        return network_ops.public_ip()
    
    def _handle_network_ping(self, params):
        host = params.get("host")
        if not host:
            return {"status": "needs_info", "message": "Kisko ping karun?"}
        return network_ops.ping(host)
    
    def _handle_network_dns(self, params):
        domain = params.get("domain")
        if not domain:
            return {"status": "needs_info", "message": "Konsa domain lookup karun?"}
        return network_ops.dns_lookup(domain)
    
    def _handle_network_info(self, params):
        return network_ops.network_info()
    
    # ═══════════════════════════════════════════════════════════════════════
    # CLIPBOARD HANDLERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_clipboard_copy(self, params):
        text = params.get("text")
        if not text:
            return {"status": "needs_info", "message": "Kya copy karun clipboard me?"}
        return system_ops.copy(text)
    
    def _handle_clipboard_get(self, params):
        return system_ops.paste()
    
    # ═══════════════════════════════════════════════════════════════════════
    # AI HANDLERS (Code Generate, Explain, Chat)
    # ═══════════════════════════════════════════════════════════════════════
    
    def _handle_code_generate(self, params):
        language = params.get("language", "python")
        description = params.get("description")
        
        if not description:
            return {"status": "needs_info", "message": "Code kya karna chahiye? (Description batao)"}
        
        from src.llm.groq_client import GroqClient
        groq = GroqClient()
        
        prompt = f"Generate {language} code for: {description}. Only provide code with comments, no explanations."
        result = groq.chat(prompt)
        
        if result.get("error"):
            return {"status": "error", "message": result["error"]}
        
        return {
            "status": "success",
            "message": f"✅ {language.upper()} code generated:",
            "data": {"code": result["response"], "language": language}
        }
    
    def _handle_explain(self, params):
        topic = params.get("topic")
        
        if not topic:
            return {"status": "needs_info", "message": "Kiske baare me batau?"}
        
        from src.llm.groq_client import GroqClient
        groq = GroqClient()
        
        prompt = f"Explain {topic} in simple terms. Be concise but informative. Use examples if helpful."
        result = groq.chat(prompt)
        
        if result.get("error"):
            return {"status": "error", "message": result["error"]}
        
        return {
            "status": "success",
            "message": result["response"]
        }
    
    def _handle_chat(self, params):
        message = params.get("message", "")
        
        from src.llm.groq_client import GroqClient
        groq = GroqClient()
        
        result = groq.chat(message)
        
        if result.get("error"):
            return {"status": "error", "message": result["error"]}
        
        return {
            "status": "success",
            "message": result["response"]
        }


# Global instance
executor = AutomationExecutor()

def execute(intent_data):
    """Execute automation"""
    return executor.execute(intent_data)