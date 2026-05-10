"""
IntelliDesk AI - Main Application Entry Point
Routes all input through SmartRouter (Auto / Chat / Agent modes)
"""

import os
import sys

# Force UTF-8 for console output on Windows to prevent logging crash with emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from src.core.conversation_manager import conversation_manager
from src.core.agentic_manager import agentic_manager
from src.core.router import router, MODE_AUTO, MODE_CHAT, MODE_AGENT
from src.utils.voice_manager import voice_manager, speak, toggle_voice, is_voice_enabled, stop_voice
from src.utils.logger import Logger
from config import Config

logger = Logger.get_logger("Main")


def format_response(result):
    """Format result for CLI display"""
    status  = result.get("status", "")
    message = result.get("message") or result.get("response", "")
    data    = result.get("data", {})
    emoji_map = {"success": "OK", "error": "ERR", "needs_info": "?", "warning": "WARN"}
    emoji  = emoji_map.get(status, ">")
    output = f"{emoji} {message}"
    if data:
        if "code" in data:
            output += f"\n\n{data['code']}"
        elif "path" in data:
            output += f"\n  {data['path']}"
    return output


def print_banner():
    print("\nIntelliDesk AI - SmartRouter Edition")
    print("Mode: Auto (auto-detect) | Chat (conversational) | Agent (task executor)")
    print("Switch: mode auto | mode chat | mode agent")
    print("-" * 60)


def print_help():
    print("\nQuick commands:")
    print("  screenshot, open notepad, volume up/down")
    print("  time, date, calculate 5+5")
    print("  google python, play music on youtube")
    print("  shutdown, lock, restart")
    print("  mode auto | mode chat | mode agent")


def run_cli():
    """Main CLI loop - all input routed through SmartRouter"""
    print_banner()
    voice_lbl = "ON" if is_voice_enabled() else "OFF"
    print(f"  Voice: {voice_lbl}")
    print(f"  Mode:  {router.mode.upper()}")
    print()

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            low = user_input.lower()

            if low in ["exit", "quit", "bye", "q"]:
                print("\nGoodbye!")
                voice_manager.cleanup()
                break

            if low == "help":
                print_help()
                continue

            if low == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                continue

            if low == "reset":
                conversation_manager.clear_history()
                agentic_manager.clear_history()
                print("History cleared!")
                continue

            if low in ["voice on", "toggle voice"]:
                enabled = toggle_voice()
                print("\nVoice: " + ("ON" if enabled else "OFF"))
                continue

            if low == "voice off":
                if is_voice_enabled():
                    toggle_voice()
                print("\nVoice OFF")
                continue

            if low in ["stop", "stop voice", "chup", "ruk"]:
                stop_voice()
                print("\nVoice stopped")
                continue

            if low.startswith("mode "):
                m = low.split()[-1]
                if m in (MODE_AUTO, MODE_CHAT, MODE_AGENT):
                    router.mode = m
                    print(f"\nSwitched to {m.upper()} mode")
                else:
                    print("\nUnknown mode. Use: mode auto | mode chat | mode agent")
                continue

            # Route through SmartRouter
            stop_voice()
            effective = router.effective_mode_for(user_input)
            print(f"\n  [{effective.upper()} mode]")

            results = router.process(user_input)

            for i, result in enumerate(results, 1):
                if len(results) > 1:
                    print(f"\n  [{i}/{len(results)}]")
                print(f"\nBot: {format_response(result)}")

                if result.get("type") == "function_call":
                    for func in result.get("functions_executed", []):
                        print(f"   -> {func['function']}()")

                if result.get("status") == "success":
                    speak(result.get("response", ""))
                elif result.get("status") == "error":
                    speak(result.get("response", ""), force=True)

                if result.get("status") in ["error", "needs_info"]:
                    break

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            voice_manager.cleanup()
            break

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n{error_msg}")
            logger.error(f"CLI error: {e}")
            speak(error_msg, force=True)


def run_gui():
    """Launch GUI mode"""
    try:
        from src.gui.spotlight_app import SpotlightApp, HAS_TRAY
        print("Launching IntelliDesk AI...")
        print("Ctrl+Space to open spotlight | F12 to toggle voice")
        print("Use the Auto/Chat/Agent pill in the UI to switch modes")
        app = SpotlightApp()
        if HAS_TRAY:
            print("System tray enabled")
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\nFailed to launch GUI: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("Falling back to CLI mode...")
        run_cli()


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
        print("\nGoodbye!")
        sys.exit(0)
