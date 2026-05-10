"""
IntelliDesk AI — Smart Router

The single entry point for ALL user input.
Decides which backend handles each request:

  MODE_AUTO  → IntentClassifier decides (chat vs agent)
  MODE_CHAT  → Always GroqClient (fast, conversational)
  MODE_AGENT → Always AgenticManager (full ReAct + tools)

The GUI stores and updates the active mode.
run.py also goes through this router.
"""

from src.core.intent_classifier import classify
from src.core.agentic_manager import agentic_manager
from src.core.conversation_manager import conversation_manager
from src.utils.logger import Logger

logger = Logger.get_logger("Router")

# Mode constants — used by both the router and the GUI toggle
MODE_AUTO  = "auto"
MODE_CHAT  = "chat"
MODE_AGENT = "agent"


class SmartRouter:
    """
    Dispatches user input to the correct backend.
    Thread-safe: mode can be changed from the GUI thread at any time.
    """

    def __init__(self):
        self._mode = MODE_AUTO  # Default: auto-detect

    # ─── Mode management ─────────────────────────────────────────────────────

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str):
        assert value in (MODE_AUTO, MODE_CHAT, MODE_AGENT), f"Invalid mode: {value}"
        self._mode = value
        logger.info(f"Router mode set to: {value.upper()}")

    # ─── Routing ─────────────────────────────────────────────────────────────

    def process(self, user_input: str) -> list:
        """
        Route user_input to the right backend and return results list.

        Returns:
            list of result dicts (same format as agentic_manager.process)
        """
        text = user_input.strip()
        if not text:
            return [{"type": "error", "response": "Please say something!", "status": "error"}]

        resolved_mode = self._resolve_mode(text)
        logger.info(f"Routing → {resolved_mode.upper()} | Input: '{text[:50]}'")

        if resolved_mode == MODE_AGENT:
            return agentic_manager.process(text)
        else:
            # Chat mode — conversation_manager returns list of results
            return conversation_manager.process(text)

    def _resolve_mode(self, text: str) -> str:
        """Resolve the effective mode for this specific input."""
        if self._mode == MODE_AUTO:
            if getattr(agentic_manager, 'is_waiting_for_info', False):
                return MODE_AGENT
            return classify(text)       # Let classifier decide
        return self._mode               # User manually selected a mode

    def effective_mode_for(self, text: str) -> str:
        """Return what mode WOULD be used (for UI indicator display)."""
        return self._resolve_mode(text)


# ─── Singleton ───────────────────────────────────────────────────────────────
router = SmartRouter()
