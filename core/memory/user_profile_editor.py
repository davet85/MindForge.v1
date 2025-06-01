import json
from pathlib import Path
from utils.constants import PROFILE_PATH, DEFAULT_PROMPT

def save_user_profile(name, bio, current_struggles, past_struggles, answers, generated_prompt):
    """Save the user profile to a JSON file."""
    profile_data = {
        "name": name,
        "bio": bio,
        "current_struggles": current_struggles,
        "past_struggles": past_struggles,
        "answers": answers,
        "generated_prompt": generated_prompt
    }

    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)  # Ensure /database/ exists

    with PROFILE_PATH.open("w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

def load_user_profile():
    """Load and return the user profile. Returns None if not found or invalid."""
    if not PROFILE_PATH.exists() or PROFILE_PATH.stat().st_size == 0:
        return None

    try:
        with PROFILE_PATH.open("r", encoding="utf-8") as f:
            profile = json.load(f)

        if not isinstance(profile, dict):
            return None

        # Ensure all expected fields are present
        profile.setdefault("name", "")
        profile.setdefault("bio", "")
        profile.setdefault("current_struggles", "")
        profile.setdefault("past_struggles", "")
        profile.setdefault("answers", [])
        profile.setdefault("generated_prompt", DEFAULT_PROMPT)

        return profile

    except (json.JSONDecodeError, OSError):
        return None
