# gpt_handler.py — GPT Interaction Logic

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from utils.constants import DEFAULT_PROMPT, PROFILE_PATH, GPT_MODEL, TEMPERATURE, MAX_TOKENS
from utils.logger import log_info, log_error

# --- Load Environment & OpenAI Client ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Load Active System Prompt ---
def load_active_prompt() -> str:
    try:
        if not PROFILE_PATH.exists() or PROFILE_PATH.stat().st_size == 0:
            log_info("User profile not found or empty. Using default prompt.")
            return DEFAULT_PROMPT

        with PROFILE_PATH.open("r", encoding="utf-8") as f:
            profile = json.load(f)

        if not isinstance(profile, dict):
            log_error("Invalid profile structure. Using default prompt.")
            return DEFAULT_PROMPT

        return profile.get("generated_prompt", DEFAULT_PROMPT)

    except json.JSONDecodeError:
        log_error("Corrupted user_profile.json. Using default prompt.")
        return DEFAULT_PROMPT

    except Exception as e:
        log_error(f"Unexpected error while loading system prompt: {e}")
        return DEFAULT_PROMPT

# --- Handle GPT Prompt Submission ---
def handle_prompt(user_input: str) -> str:
    try:
        system_prompt = load_active_prompt()

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input.strip()}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

        if not response.choices:
            log_error("OpenAI returned no choices.")
            return "⚠️ GPT did not return a valid response."

        return response.choices[0].message.content.strip()

    except OpenAIError as e:
        log_error(f"OpenAI API error: {e}")
        return "⚠️ GPT unavailable. Check API key or usage limits."

    except Exception as e:
        log_error(f"Unhandled GPT error: {e}")
        return "⚠️ Internal error during reflection."
