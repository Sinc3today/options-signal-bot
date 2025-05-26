import os
import csv
from datetime import datetime
from price_data import get_recent_price_data

# File paths (match project layout)
PENDING_FILE = "output/logs/pending_entries.csv"
LOG_FILE = "output/logs/entry_log.txt"

def log(message):
    """
    Logs a message to output/logs/entry_log.txt with UTF-8 encoding.
    Automatically creates the output/logs directory if it doesn't exist.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {message}\n")
    except Exception as e:
        print(f"[Log Error] Could not write log entry: {e}")


def get_current_price(symbol):
    """
    Uses get_recent_price_data() from price_data module to return the latest price for a symbol.
    Assumes result has a 'Close' column.
    """
    try:
        df = get_recent_price_data(symbol)
        if df is not None and not df.empty:
            return df["Close"].iloc[-1].item()  # Future-proof pandas float
    except Exception as e:
        log(f"[ERROR] Failed to fetch price for {symbol}: {e}")
    return None


def load_pending_entries():
    """
    Loads pending entries from CSV. Each row is a dict.
    """
    entries = []
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, mode="r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                entries.append(row)
    else:
        log(f"[WARNING] No pending entries file found: {PENDING_FILE}")
    return entries


def save_pending_entries(entries):
    """
    Overwrites the pending entries file with the updated list.
    """
    if not entries:
        return
    with open(PENDING_FILE, mode="w", newline="") as csvfile:
        fieldnames = entries[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)


def check_pending_entries():
    """
    Evaluates each pending entry. Updates 'Status' field to prevent duplicates.
    If conditions are met, marks as 'entered'. If not, leaves as 'waiting'.
    """
    all_entries = load_pending_entries()
    updated_entries = []

    for entry in all_entries:
        symbol = entry.get("Symbol")
        status = entry.get("Status", "waiting").lower()
        direction = entry.get("Direction", "bullish").lower()

        if status == "entered":
            updated_entries.append(entry)  # already processed
            continue

        try:
            trigger_price = float(entry.get("Trigger Price", 0))
        except ValueError:
            log(f"[ERROR] Invalid trigger price for {symbol}. Skipping.")
            entry["Status"] = "waiting"
            updated_entries.append(entry)
            continue

        current_price = get_current_price(symbol)

        if current_price is None:
            log(f"[SKIP] {symbol} — could not fetch current price")
            entry["Status"] = "waiting"
            updated_entries.append(entry)
            continue

        # Evaluate trigger condition
        triggered = (
            direction == "bullish" and current_price >= trigger_price or
            direction == "bearish" and current_price <= trigger_price
        )

        if triggered:
            log(f"[ENTRY ✅] {symbol} triggered @ {current_price} (Target: {trigger_price})")
            entry["Status"] = "entered"
            # Optional: mark_trade_entry(...)
        else:
            entry["Status"] = "waiting"

        updated_entries.append(entry)  # Always add entry back with updated status

    save_pending_entries(updated_entries)


if __name__ == "__main__":
    check_pending_entries()
