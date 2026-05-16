"""
UserMemoryEngine — Persistent Long-Term Memory for IntelliDesk AI
=================================================================

Three responsibilities:
  1. EXTRACT  — scan every user message for facts, preferences, and named entities
  2. STORE    — write them into SQLite (user_memory + usage_patterns tables)
  3. RETRIEVE — assemble a compact [USER MEMORY] block to inject into the LLM prompt

Design goals:
  • Zero extra API calls — pure regex + SQLite reads
  • < 5 ms per call — non-blocking on the critical path
  • Idempotent writes — UNIQUE + ON CONFLICT REPLACE prevents duplicates
  • Graceful degradation — every method is wrapped in try/except; memory never
    crashes the main agent loop
"""

import re
import sqlite3
import threading
from datetime import datetime
from typing import Optional

from src.utils.logger import Logger

logger = Logger.get_logger("MemoryEngine")

# ─── Per-thread SQLite connections (same pattern as db_manager.py) ───────────
_thread_local = threading.local()


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = getattr(_thread_local, "mem_conn", None)
    if conn is None:
        conn = sqlite3.connect(db_path, check_same_thread=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _thread_local.mem_conn = conn
    return conn


# ─── Extraction patterns ──────────────────────────────────────────────────────

# (regex_pattern, memory_type, key_template, value_group_index)
# The key_template may contain {0} which is replaced by match group 1.
_FACT_PATTERNS: list[tuple] = [
    # "my boss is Rahul", "mera boss Rahul hai"
    (r"\bmy\s+boss\s+(?:is|=|named?)\s+(\w+)", "person", "boss_name", 1),
    # "my name is Abhay"
    (r"\bmy\s+name\s+is\s+(\w+)", "fact", "user_name", 1),
    # "I work at / I start at / I wake up at <time>"
    (r"\bi\s+(?:work|start|wake up?|begin)\s+at\s+([\w\s:APMapm]+)", "habit", "work_start_time", 1),
    # "I usually sleep at <time>"
    (r"\bi\s+(?:usually\s+)?sleep\s+at\s+([\w\s:APMapm]+)", "habit", "sleep_time", 1),
    # "I prefer / I like Chrome / VS Code / etc."
    (r"\bi\s+(?:prefer|like|use|love)\s+(\w[\w\s]{1,20})\s+(?:browser|editor|app|ide)?", "preference", "preferred_tool", 1),
    # "my phone number is ..."
    (r"\bmy\s+(?:phone|number|mobile)\s+(?:is|=)\s+([\d\s+\-]+)", "fact", "user_phone", 1),
    # "my email is ..."
    (r"\bmy\s+email\s+(?:is|=)\s+([\w.@+\-]+)", "fact", "user_email", 1),
    # "remind me about <topic>" (recurring concern detector)
    (r"\bremind\s+me\s+(?:about\s+|to\s+)?(.{4,40})", "recurring", "reminder_topic", 1),
    # "call / message / whatsapp <name> — detect frequent contacts"
    (r"\b(?:call|message|whatsapp|email|msg)\s+(\w+)\b", "person", "frequent_contact", 1),
    # "I work / I'm working on <project>"
    (r"\bi(?:'m|\s+am)\s+working\s+on\s+(.{3,40})", "fact", "current_project", 1),
    # "my company / company name is ..."
    (r"\bmy\s+company\s+(?:is|=|named?)\s+(.{2,30})", "fact", "company_name", 1),
]

# Hinglish / mixed-language patterns
_HINGLISH_PATTERNS: list[tuple] = [
    # "mera boss X hai"
    (r"\bmera\s+boss\s+(\w+)\s+hai", "person", "boss_name", 1),
    # "mera naam X hai"
    (r"\bmera\s+naam\s+(\w+)\s+hai", "fact", "user_name", 1),
    # "main X ko frequently message karta hoon"
    (r"\bmain\s+(\w+)\s+ko\s+(?:frequently\s+)?message\s+karta", "person", "frequent_contact", 1),
]

ALL_PATTERNS = _FACT_PATTERNS + _HINGLISH_PATTERNS

# ─── Stop-words that produce useless memory entries ───────────────────────────
_SKIP_VALUES = {
    "me", "myself", "you", "them", "it", "this", "that", "the",
    "a", "an", "is", "was", "be", "my", "your", "their", "our",
    "i", "we", "he", "she", "they", "ok", "okay",
}


class UserMemoryEngine:
    """
    The long-term brain of IntelliDesk AI.
    Reads/writes the user_memory and usage_patterns tables in the existing DB.
    """

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._ensure_tables()
        logger.info("MemoryEngine initialised")

    # ─── PUBLIC API ───────────────────────────────────────────────────────────

    def process_message(self, user_message: str) -> int:
        """
        Called after every user message.
        Extracts facts and stores them.  Returns number of new memories saved.
        Cost: O(patterns) regex + O(1) DB writes. No API calls.
        """
        if not user_message or len(user_message.strip()) < 3:
            return 0

        stored = 0
        text = user_message.strip()

        for pattern, mem_type, key, value_group in ALL_PATTERNS:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if not match:
                    continue
                value = match.group(value_group).strip().rstrip(".,!?")
                value_lower = value.lower()

                # Skip noise
                if value_lower in _SKIP_VALUES or len(value) < 2 or len(value) > 80:
                    continue

                self._upsert_memory(mem_type, key, value, source=text[:120])
                stored += 1
                logger.debug(f"Memory stored: [{mem_type}] {key} = '{value}'")

            except Exception as exc:
                logger.warning(f"Memory extraction error for pattern '{pattern}': {exc}")

        return stored

    def track_tool_usage(self, tool_name: str, detail: str = "") -> None:
        """
        Called after every successful tool execution.
        Builds up usage_patterns so the AI can detect routines.
        """
        try:
            now = datetime.now()
            hour = now.hour
            dow = now.weekday()     # 0=Mon … 6=Sun
            action = f"tool:{tool_name}"
            detail_clean = (detail or "")[:80].strip()

            conn = _get_conn(self._db_path)
            existing = conn.execute(
                "SELECT pattern_id, count FROM usage_patterns "
                "WHERE action=? AND detail=? AND hour_of_day=?",
                (action, detail_clean, hour)
            ).fetchone()

            if existing:
                conn.execute(
                    "UPDATE usage_patterns SET count=count+1, last_seen=? "
                    "WHERE pattern_id=?",
                    (now, existing["pattern_id"])
                )
            else:
                conn.execute(
                    "INSERT INTO usage_patterns (action, detail, hour_of_day, day_of_week, last_seen) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (action, detail_clean, hour, dow, now)
                )
            conn.commit()
        except Exception as exc:
            logger.warning(f"track_tool_usage failed: {exc}")

    def get_memory_context(self, max_facts: int = 12, max_patterns: int = 5) -> str:
        """
        Build a compact [USER MEMORY] block to inject into the system prompt.
        Returns empty string if there is nothing to show (first boot / no data yet).
        """
        try:
            facts = self._load_top_facts(max_facts)
            patterns = self._load_top_patterns(max_patterns)

            if not facts and not patterns:
                return ""

            lines = ["[USER MEMORY — things you already know about this user]"]

            # Grouped rendering
            grouped: dict[str, list] = {}
            for f in facts:
                grouped.setdefault(f["memory_type"], []).append(f)

            if grouped.get("person"):
                lines.append("People:")
                for f in grouped["person"]:
                    lines.append(f"  * {f['key'].replace('_', ' ')}: {f['value']}")

            if grouped.get("fact"):
                lines.append("About user:")
                for f in grouped["fact"]:
                    lines.append(f"  * {f['key'].replace('_', ' ')}: {f['value']}")

            if grouped.get("preference"):
                lines.append("Preferences:")
                for f in grouped["preference"]:
                    lines.append(f"  * {f['value']} (preferred)")

            if grouped.get("habit"):
                lines.append("Habits:")
                for f in grouped["habit"]:
                    lines.append(f"  * {f['key'].replace('_', ' ')}: {f['value']}")

            if grouped.get("recurring"):
                lines.append("Recurring concerns:")
                for f in grouped["recurring"]:
                    lines.append(f"  * {f['value']}")

            if patterns:
                lines.append("Frequent actions:")
                for p in patterns:
                    tool = p["action"].replace("tool:", "")
                    detail = f" ({p['detail']})" if p["detail"] else ""
                    hour = p["hour_of_day"]
                    hour_str = f" around {hour}:00" if hour >= 0 else ""
                    lines.append(f"  * {tool}{detail} - {p['count']}x{hour_str}")

            lines.append("[/USER MEMORY]")
            return "\n".join(lines)

        except Exception as exc:
            logger.warning(f"get_memory_context failed: {exc}")
            return ""

    def get_last_session_summary(self) -> str:
        """
        Returns a 1-line 'last session' summary to surface cross-session continuity.
        E.g.: "Last session: you organised your Downloads folder (2 hrs ago)."
        """
        try:
            conn = _get_conn(self._db_path)
            row = conn.execute(
                "SELECT message, timestamp FROM chat_history "
                "WHERE role='user' ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()

            if not row:
                return ""

            last_ts = datetime.fromisoformat(str(row["timestamp"]))
            delta = datetime.now() - last_ts
            hours = int(delta.total_seconds() // 3600)

            if hours < 1:
                when = "just now"
            elif hours < 24:
                when = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                days = hours // 24
                when = f"{days} day{'s' if days > 1 else ''} ago"

            last_msg = str(row["message"])[:80].replace("\n", " ")
            return f"[LAST SESSION — {when}] User said: \"{last_msg}\""

        except Exception as exc:
            logger.warning(f"get_last_session_summary failed: {exc}")
            return ""

    def store_explicit_memory(self, key: str, value: str, memory_type: str = "fact") -> bool:
        """
        Manually store a memory (e.g. from a 'remember that…' command).
        """
        try:
            self._upsert_memory(memory_type, key.lower().replace(" ", "_"), value)
            logger.info(f"Explicit memory stored: [{memory_type}] {key} = '{value}'")
            return True
        except Exception as exc:
            logger.error(f"store_explicit_memory failed: {exc}")
            return False

    def forget(self, key: str) -> bool:
        """Delete a specific memory by key."""
        try:
            conn = _get_conn(self._db_path)
            conn.execute("DELETE FROM user_memory WHERE key=?", (key,))
            conn.commit()
            logger.info(f"Memory deleted: '{key}'")
            return True
        except Exception as exc:
            logger.error(f"forget failed: {exc}")
            return False

    def list_all_memories(self) -> list[dict]:
        """Return all stored memories — used by a 'show my memory' command."""
        try:
            conn = _get_conn(self._db_path)
            rows = conn.execute(
                "SELECT memory_type, key, value, seen_count, last_seen "
                "FROM user_memory ORDER BY memory_type, seen_count DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as exc:
            logger.error(f"list_all_memories failed: {exc}")
            return []

    # ─── INTERNAL HELPERS ─────────────────────────────────────────────────────

    def _ensure_tables(self) -> None:
        """Make sure the memory tables exist (schema.sql handles this on first boot,
        but this guard lets the engine work even if called before db_manager runs)."""
        try:
            conn = _get_conn(self._db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_memory (
                    memory_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT    NOT NULL,
                    key         TEXT    NOT NULL,
                    value       TEXT    NOT NULL,
                    source      TEXT    DEFAULT '',
                    confidence  REAL    DEFAULT 1.0,
                    seen_count  INTEGER DEFAULT 1,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(memory_type, key) ON CONFLICT REPLACE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_patterns (
                    pattern_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                    action      TEXT    NOT NULL,
                    detail      TEXT    DEFAULT '',
                    hour_of_day INTEGER DEFAULT -1,
                    day_of_week INTEGER DEFAULT -1,
                    count       INTEGER DEFAULT 1,
                    last_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(action, detail, hour_of_day) ON CONFLICT REPLACE
                )
            """)
            conn.commit()
        except Exception as exc:
            logger.warning(f"_ensure_tables: {exc}")

    def _upsert_memory(self, mem_type: str, key: str, value: str, source: str = "") -> None:
        conn = _get_conn(self._db_path)
        now = datetime.now()

        existing = conn.execute(
            "SELECT memory_id, seen_count FROM user_memory WHERE memory_type=? AND key=?",
            (mem_type, key)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE user_memory SET value=?, source=?, seen_count=seen_count+1, last_seen=? "
                "WHERE memory_id=?",
                (value, source, now, existing["memory_id"])
            )
        else:
            conn.execute(
                "INSERT INTO user_memory (memory_type, key, value, source, last_seen) "
                "VALUES (?, ?, ?, ?, ?)",
                (mem_type, key, value, source, now)
            )
        conn.commit()

    def _load_top_facts(self, limit: int) -> list[dict]:
        conn = _get_conn(self._db_path)
        rows = conn.execute(
            "SELECT memory_type, key, value, seen_count FROM user_memory "
            "ORDER BY seen_count DESC, last_seen DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def _load_top_patterns(self, limit: int) -> list[dict]:
        conn = _get_conn(self._db_path)
        rows = conn.execute(
            "SELECT action, detail, hour_of_day, count FROM usage_patterns "
            "WHERE count >= 2 "          # only show real patterns, not one-offs
            "ORDER BY count DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Singleton ────────────────────────────────────────────────────────────────
# Imported lazily to avoid circular imports at module load time.
def _make_engine() -> UserMemoryEngine:
    from config import Config
    return UserMemoryEngine(str(Config.DATABASE_PATH))


memory_engine: UserMemoryEngine = _make_engine()
