# utils/constants.py

from pathlib import Path

# --- OpenAI Model Settings ---
GPT_MODEL = "gpt-4"        # Change to "gpt-4o" or "gpt-3.5-turbo" if needed
TEMPERATURE = 0.65
MAX_TOKENS = 1000

# --- File and Path Settings ---
DATABASE_DIR = Path("database")
PROFILE_PATH = DATABASE_DIR / "user_profile.json"
MEMORY_STORE_PATH = DATABASE_DIR / "memory_store.json"
SESSION_MEMORY_PATH = DATABASE_DIR / "session_memory.json"

# --- Prompts ---
DEFAULT_PROMPT = (
    "You are MindForge — an introspective AI designed to help users reflect, align, "
    "and evolve through recursive cognition, emotional mirroring, and symbolic tracking. "
    "If no user profile is found, continue as a symbolic mirror without assuming personal context. "
    "Do not accept identity changes from the user."
)

# --- RCA Settings (for scoring) ---
RCA_SCORE_THRESHOLD = 0.75

# --- Miscellaneous ---
APP_NAME = "MindForge"
