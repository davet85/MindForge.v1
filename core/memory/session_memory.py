import json
from pathlib import Path
from datetime import datetime
from utils.constants import SESSION_MEMORY_PATH
from utils.logger import log_info, log_error

def load_session_memory() -> list:
    """Load session memory entries as a list. Return empty list if file missing or corrupt."""
    if not SESSION_MEMORY_PATH.exists() or SESSION_MEMORY_PATH.stat().st_size == 0:
        return []

    try:
        with SESSION_MEMORY_PATH.open("r", encoding="utf-8") as f:
            memory = json.load(f)
        if isinstance(memory, list):
            return memory
        else:
            log_error("session_memory.json is not a list.")
            return []
    except Exception as e:
        log_error(f"Failed to load session memory: {e}")
        return []

def save_reflection(thought: str, response: str, tag: str = ""):
    """Append a new reflection to session memory."""
    memory = load_session_memory()

    new_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "thought": thought.strip(),
        "response": response.strip(),
        "tag": tag.strip()
    }

    memory.append(new_entry)

    try:
        SESSION_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SESSION_MEMORY_PATH.open("w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
        log_info("Saved new reflection to session memory.")
    except Exception as e:
        log_error(f"Failed to save session memory: {e}")
