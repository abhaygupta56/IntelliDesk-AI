"""
═══════════════════════════════════════════════════════════════════════════════
INTELLIDESK AI - MAIN APPLICATION
Fixed: Uses new conversation_manager system
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys

# Set up path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SYSTEM IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════
from src.core.conversation_manager import conversation_manager
from src.utils.voice_manager import voice_manager, speak, toggle_voice, is_voice_enabled, stop_voice
from src.utils.logger import Logger

logger = Logger.get_logger("Main")


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATTING & DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def format_response(result):
    """Format result for CLI display"""
    status = result.get("status", "")
    message = result.get("message", "")
    data = result.get("data", {})
    
    # Emoji based on status
    emoji_map = {
        "success": "✅",
        "error": "❌",
        "needs_info": "❓",
        "warning": "⚠️"
    }
    emoji = emoji_map.get(status, "💬")
    
    output = f"{emoji} {message}"
    
    # Add data details
    if data:
        if "code" in data:
            output += f"\n\n```{data.get('language', '')}\n{data['code']}\n```"
        elif "results" in data:
            output += f"\n  Found {len(data['results'])} items"
        elif "path" in data:
            output += f"\n  📁 {data['path']}"
    
    return output


def print_banner():
    """Print welcome banner"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██╗███╗   ██╗████████╗███████╗██╗     ██╗     ██╗██████╗ ███████╗███████╗  ║
║   ██║████╗  ██║╚══██╔══╝██╔════╝██║     ██║     ██║██╔══██╗██╔════╝██╔════╝  ║
║   ██║██╔██╗ ██║   ██║   █████╗  ██║     ██║     ██║██║  ██║█████╗  ███████╗  ║
║   ██║██║╚██╗██║   ██║   ██╔══╝  ██║     ██║     ██║██║  ██║██╔══╝  ╚════██║  ║
║   ██║██║ ╚████║   ██║   ███████╗███████╗███████╗██║██████╔╝███████╗███████║  ║
║   ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝╚═════╝ ╚══════╝╚══════╝  ║
║                                                                              ║
║                    🤖 AI-Powered Desktop Automation 🤖                       ║
║                    62+ Functions | Hinglish | Voice Enabled                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    print("  💡 Commands: Type any command in English or Hinglish")
    print("  📝 Examples: 'screenshot', 'time kya hai', 'open chrome then search python'")
    print("  🎙️  Voice:   'voice on' | 'voice off' | 'toggle voice' | 'stop voice'")
    print("  ⚙️  Special:  'help' | 'stats' | 'clear' | 'reset' | 'exit'")
    print("─" * 78)


def print_help():
    """Print help message"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              QUICK COMMANDS                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  💻 System:     shutdown | restart | lock | sleep | system info              ║
║  📸 Screenshot: screenshot | ss                                              ║
║  🔊 Volume:     volume up | volume down                                      ║
║  ⏰ Time:       time | date | calculate 5+5                                  ║
║  📁 Files:      create file test.txt | delete file x | organize downloads    ║
║  🌐 Web:        google python | open youtube | weather                       ║
║  🪟 Window:     minimize | maximize | close window                           ║
║  ⌨️  Type:      type hello world                                            ║
║  🎵 Media:      play python tutorial on youtube                             ║
║  💻 Code:       write python code for bubble sort (uses Ollama)             ║
║  🔗 Multi:      open chrome then search python | volume up then lock        ║
║  🎙️  Voice:     voice on | voice off | toggle voice                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI MODE
# ═══════════════════════════════════════════════════════════════════════════════

def run_cli():
    """Main CLI loop using new conversation manager"""
    print_banner()
    
    voice_status = "🔊 ON" if is_voice_enabled() else "🔇 OFF"
    print(f"  Voice Status: {voice_status}")
    print()
    
    while True:
        try:
            user_input = input("\n🎯 You: ").strip()
            
            if not user_input:
                continue
            
            # ══════════════════════════════════════════════════════════════
            # SPECIAL COMMANDS
            # ══════════════════════════════════════════════════════════════
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Goodbye! IntelliDesk AI shutting down...")
                voice_manager.cleanup()
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            if user_input.lower() == 'stats':
                stats = conversation_manager.get_stats()
                print(f"\n📊 Conversation Stats:")
                print(f"   Messages in history: {stats['messages_in_history']}")
                print(f"   Groq history size: {stats['groq_history']}")
                continue
            
            if user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                print_banner()
                continue
            
            if user_input.lower() == 'reset':
                conversation_manager.clear_history()
                print("🔄 Conversation history cleared!")
                continue
            
            if user_input.lower() in ['voice on', 'voice off', 'toggle voice']:
                enabled = toggle_voice()
                status = "🔊 Voice enabled" if enabled else "🔇 Voice disabled"
                print(f"\n{status}")
                continue

            if user_input.lower() in ['stop', 'stop voice', 'chup', 'ruk']:
                stop_voice()
                print("\n🔇 Voice stopped")
                continue

            
            # ══════════════════════════════════════════════════════════════
            # PROCESS COMMAND (NEW SYSTEM)
            # ══════════════════════════════════════════════════════════════

            stop_voice()
            
            results = conversation_manager.process(user_input)
            
            # Display all results
            for i, result in enumerate(results, 1):
                if len(results) > 1:
                    print(f"\n   [{i}/{len(results)}]")
                
                response = format_response(result)
                print(f"\n🤖 Bot: {response}")
                
                # Show function execution details
                if result.get('type') == 'function_call':
                    functions = result.get('functions_executed', [])
                    for func in functions:
                        func_name = func['function']
                        func_args = func['arguments']
                        print(f"      → Executed: {func_name}({func_args})")
                
                # Voice output
                if result.get('status') == 'success':
                    speak(result.get('response', ''))
                elif result.get('status') == 'error':
                    speak(result.get('response', ''), force=True)
                
                # Stop on error/needs_info
                if result.get('status') in ['error', 'needs_info']:
                    break
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            voice_manager.cleanup()
            break
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n❌ {error_msg}")
            logger.error(f"CLI error: {e}")
            speak(error_msg, force=True)


# ═══════════════════════════════════════════════════════════════════════════════
# GUI MODE
# ═══════════════════════════════════════════════════════════════════════════════

def run_gui():
    """Launch GUI mode"""
    try:
        from src.gui.spotlight_app import SpotlightApp, HAS_TRAY
        import threading
        
        print("🚀 Launching IntelliDesk AI in Background...")
        print("💡 TIP: Press 'Ctrl + Space' anytime to open the spotlight!")
        print("💡 TIP: Press 'F12' to toggle voice on/off")
        
        app = SpotlightApp()
        
        if HAS_TRAY:
            print("✅ System tray enabled")
        
        app.run()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Shutting down...")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n──────────────────────────────────────────────────")
        print(f"❌ Failed to launch GUI: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"──────────────────────────────────────────────────\n")
        print("Falling back to CLI mode...\n")
        run_cli()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Shutting down...")
        sys.exit(0)