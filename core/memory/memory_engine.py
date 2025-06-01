import json
import pandas as pd
from utils.constants import MEMORY_STORE_PATH
from utils.logger import log_info, log_error

def calculate_alignment_score(memory: list) -> float:
    """
    Calculate the average alignment score between thought and response.
    Alignment is defined as inverse deviation in text length, scaled [0.0, 1.0].
    """
    try:
        if not memory or not isinstance(memory, list):
            return 0.0

        df = pd.DataFrame(memory)
        if "thought" not in df.columns or "response" not in df.columns:
            return 0.0

        df["thought_len"] = df["thought"].apply(lambda x: len(str(x)))
        df["response_len"] = df["response"].apply(lambda x: len(str(x)))

        df["alignment"] = 1.0 - (
            abs(df["thought_len"] - df["response_len"]) /
            df[["thought_len", "response_len"]].max(axis=1).replace(0, 1)
        )
        df["alignment"] = df["alignment"].clip(0.0, 1.0)

        score = round(df["alignment"].mean(), 3)
        return score

    except Exception as e:
        log_error(f"Failed to calculate alignment score: {e}")
        return 0.0

def load_memory_for_analysis() -> list:
    """
    Load memory store from file for alignment/trend analysis.
    Returns list of reflection entries or empty list if missing.
    """
    try:
        if not MEMORY_STORE_PATH.exists():
            return []

        with open(MEMORY_STORE_PATH, "r", encoding="utf-8") as f:
            memory = json.load(f)

        if isinstance(memory, list):
            return memory
        else:
            log_error("Memory file does not contain a list.")
            return []

    except Exception as e:
        log_error(f"Error loading memory store: {e}")
        return []
