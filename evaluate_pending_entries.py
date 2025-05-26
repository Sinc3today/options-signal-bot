# evaluate_pending_entries.py

from pending_entry_queue import update_pending_status
from entry_exit_tracker import log_entry
from price_data import get_recent_price_data
import pandas as pd
from datetime import datetime
import re

LOG_PATH = "output/logs/tasklog.txt"

def strip_emoji(text):
    emoji_pattern = re.compile(
        "[" "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\u2600-\u26FF"
        "\u2700-\u27BF" "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def log(message):
    timestamped = f"[{datetime.now()}] {message}"
    print(timestamped)  # keep emojis in terminal
    safe = strip_emoji(timestamped)

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(safe + "\n")

PENDING_CSV = "output/logs/pending_entries.csv"

def log(message):
    with open("output/logs/tasklog.txt", "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def parse_price_condition(entry_condition):
    try:
        return float(entry_condition.split()[2])
    except Exception as e:
        log(f"[ERROR] Failed to parse trigger price from: {entry_condition} | {e}")
        return None

def check_pending_entries():
    try:
        df = pd.read_csv(PENDING_CSV)
    except FileNotFoundError:
        log("[PENDING] No pending entries file found.")
        return

    waiting_entries = df[df["Status"] == "waiting"]

    if waiting_entries.empty:
        log("[PENDING] No pending trades to evaluate.")
        return

    for _, row in waiting_entries.iterrows():
        symbol = row["Symbol"]
        trend = row["Signal Trend"]
        trigger_price = parse_price_condition(row["Entry Condition"])
        signal_time = row["Signal Source Time"]

        if not trigger_price:
            log(f"[SKIP] {symbol}: Could not parse entry condition.")
            continue

        try:
            df_price = get_recent_price_data(symbol, interval="5m", period="1d")

            if df_price.empty or "Close" not in df_price.columns:
                log(f"[SKIP] {symbol}: No recent price data.")
                continue

            current_price = float(df_price["Close"].iloc[-1].item())
        except Exception as e:
            log(f"[ERROR] Failed to retrieve price for {symbol}: {e}")
            continue

        if current_price >= trigger_price:
            log_entry(
                symbol=symbol,
                entry_price=current_price,
                buffer="0.5%",
                rationale=row["Entry Condition"],
                expectation=f"{trend} trend continuation",
                signal_time=signal_time,
                trend=trend
            )
            update_pending_status(
                symbol=symbol,
                new_status="entered",
                entry_price=current_price,
                notes="Auto-triggered by price breakout"
            )
            log(f"[ENTRY ✅] {symbol} entered @ {current_price}")
        else:
            log(f"[WAIT] {symbol}: {current_price} < {trigger_price}")

if __name__ == "__main__":
    check_pending_entries()
