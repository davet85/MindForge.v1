import os
import datetime

LOG_FILE = os.getenv("MINDFORGE_LOG_FILE", "mindforge.log")

def log_info(message: str):
    _log("INFO", message)

def log_error(message: str):
    _log("ERROR", message)

def _log(level: str, message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"

    # Print to console
    print(log_line)

    # Append to log file
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"[LOGGER ERROR] Could not write to log file: {e}")

# --- Optional: Usage example ---
if __name__ == "__main__":
    log_info("Logger initialized successfully.")
    log_error("Sample error for testing.")
