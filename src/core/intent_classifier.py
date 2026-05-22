"""
Intent Classifier — Zero-cost, zero-latency intent detection.

Classifies user input into one of three modes:
  - "chat"  → Conversational / question → route to GroqClient
  - "agent" → Task / action / command   → route to AgenticManager
  - "auto"  → Ambiguous (fallback: chat)

No API calls. Pure rule-based matching. Runs in <1ms.
"""

import re
from src.utils.logger import Logger

logger = Logger.get_logger("IntentClassifier")


# ─── Signals that strongly indicate TASK / ACTION ────────────────────────────

AGENT_VERBS = {
    # App control
    "open", "close", "launch", "start", "run", "execute", "quit", "kill",
    # File ops
    "create", "delete", "move", "copy", "rename", "save", "write", "read",
    "make", "remove", "find", "search", "organize",
    # Web
    "google", "search", "browse", "go to", "visit", "download",
    # Media
    "play", "pause", "stop", "skip", "next", "previous", "mute", "unmute",
    "volume",
    # System
    "shutdown", "restart", "reboot", "lock", "sleep", "hibernate", "logout",
    "screenshot", "capture", "record",
    # Communication
    "send", "message", "email", "whatsapp", "call", "notify",
    # Utilities
    "set", "schedule", "remind", "timer", "alarm", "calculate", "convert",
    "translate", "type", "click", "press", "scroll", "zoom",
    # Window
    "minimize", "maximize", "resize", "move", "switch", "focus",
    # Sentry
    "watch", "monitor", "sentry", "surveillance",
    # Note
    "note", "jot", "bookmark",
    # Clipboard
    "paste", "copy",
    # General Display
    "show", "display",
}

# Words that suggest the user is asking a QUESTION / wants CONVERSATION
CHAT_SIGNALS = {
    # Greetings
    "hey", "hi", "hello", "hiya", "yo", "sup", "wassup", "howdy",
    "namaste", "helo", "hii", "hiii",
    # Farewells
    "bye", "goodbye", "goodnight", "take care",
    # Thanks
    "thanks", "thank you", "shukriya", "dhanyawad", "thx",
    # Identity / capability questions
    "who are you", "what are you", "what can you do", "tell me about yourself",
    "your name", "who made you", "aap kaun", "tumhara naam",
    # Pure info questions (without action intent)
    "what is", "what's", "whats", "who is", "who's", "where is", "when is",
    "how does", "how do", "why is", "explain", "describe", "tell me",
    "samjhao", "batao", "kya hai", "kaisa", "kyun", "kaise", "kya",
    # Feedback / feelings
    "good", "great", "nice", "cool", "awesome", "okay", "ok", "fine",
    "bad", "horrible", "not good",
}

# Patterns that strongly override to AGENT mode regardless of other signals
AGENT_PATTERNS = [
    r"\bopen\s+\w+",                        # open <app>
    r"\bplay\s+.+on\s+youtube",             # play X on youtube
    r"\b(volume|brightness)\s+(up|down)",    # volume/brightness up/down
    r"\bsend\s+(a\s+)?(message|msg|wa|whatsapp)",  # send message/whatsapp
    r"\bset\s+(a\s+)?(timer|alarm|reminder)", # set timer/alarm/reminder
    r"\b(shutdown|restart|reboot|lock|sleep)\b",   # power ops
    r"\btake\s+a?\s*screenshot",            # take screenshot
    r"\brecord\s+(the\s+)?(screen|video|audio|window)?", # record screen/video
    r"\bsearch\s+.+\s+(on|in)\s+",         # search X on/in Y
    r"\bschedule\s+",                       # schedule anything
    r"\bdownload\s+",                       # download
    r"\b(minimize|maximize|close)\s+",      # window ops
    r"\btype\s+.{3,}",                      # type something
]

# Regex compiled once at module load
_AGENT_PATTERNS_COMPILED = [re.compile(p, re.IGNORECASE) for p in AGENT_PATTERNS]


def classify(text: str) -> str:
    """
    Classify user input.

    Returns:
        "chat"  → Conversational, answer directly
        "agent" → Task/action, use the full ReAct loop
    """
    if not text or not text.strip():
        return "chat"

    raw = text.strip().lower()

    # ── 1. Check hard-coded AGENT regex patterns first (highest priority) ──
    for pattern in _AGENT_PATTERNS_COMPILED:
        if pattern.search(raw):
            logger.debug(f"Classified as AGENT (pattern match): '{text[:40]}'")
            return "agent"

    # ── 2. Tokenize to words ───────────────────────────────────────────────
    words = set(re.findall(r"\b\w+\b", raw))

    # ── 3. Check for CHAT signals (greetings, pure questions) ─────────────
    #    Only if input is SHORT (≤6 words) — long inputs rarely stay chatty
    word_list = re.findall(r"\b\w+\b", raw)
    is_short = len(word_list) <= 6

    if is_short:
        for signal in CHAT_SIGNALS:
            if " " in signal:
                if re.search(r"\b" + re.escape(signal) + r"\b", raw):
                    logger.debug(f"Classified as CHAT (signal: '{signal}'): '{text[:40]}'")
                    return "chat"
            else:
                if signal in words:
                    logger.debug(f"Classified as CHAT (signal: '{signal}'): '{text[:40]}'")
                    return "chat"

    # ── 4. Check for AGENT verbs ──────────────────────────────────────────
    matched_verbs = AGENT_VERBS.intersection(words)
    if matched_verbs:
        logger.debug(f"Classified as AGENT (verbs: {matched_verbs}): '{text[:40]}'")
        return "agent"

    # ── 5. Heuristic: question words without action → chat ────────────────
    question_starters = {"what", "who", "where", "when", "why", "how", "is", "are",
                         "can", "kya", "kaun", "kab", "kyun", "kaise", "hai"}
    if words.intersection(question_starters) and not matched_verbs:
        logger.debug(f"Classified as CHAT (question heuristic): '{text[:40]}'")
        return "chat"

    # ── 6. Default: chat is the safer fallback ────────────────────────────
    logger.debug(f"Classified as CHAT (default): '{text[:40]}'")
    return "chat"
