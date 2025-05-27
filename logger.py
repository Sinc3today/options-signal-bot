import os
from datetime import datetime
import re

from config import LOG_PATH

def strip_emoji(text):
    emoji_pattern = re.compile(r"["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\u2600-\u26FF"
        "\u2700-\u27BF" "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def log(message):
    timestamped = f"[{datetime.now()}] {message}"
    print(timestamped)
    safe_message = strip_emoji(timestamped)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(safe_message + "\n")
