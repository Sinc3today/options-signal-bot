import os
import csv
from price_data import get_recent_price_data  # Fetches latest 1-minute OHLC data
from logger import log  # Centralized logging

# File paths (used for tracking pending and confirmed entries)
PENDING_FILE = "output/logs/pending_entries.csv"
LOG_FILE = "output/logs/entry_log.txt"

def get_current_price(symbol):
    """
    Gets the most recent price from yfinance using get_recent_price_data().
    Returns float or None if unavailable.
    """
    try:
        df = get_recent_price_data(symbol)
        if df is not None and not df.empty:
            return df["Close"].iloc[-1].item()
    except Exception as e:
        log(f"[ERROR] Failed to fetch price for {symbol}: {e}")
    return None

def load_pending_entries():
    """
    Loads entries from the pending_entries.csv file.
    Each row is returned as a dict.
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
    Saves the updated list of pending entries back to CSV.
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
    Core logic that reviews all pending trades:
    - Loads entries from CSV
    - Checks if current price meets the trigger condition
    - If so, marks as 'entered' and logs it
    """
    all_entries = load_pending_entries()
    updated_entries = []

    for entry in all_entries:
        symbol = entry.get("Symbol")
        status = entry.get("Status", "waiting").lower()
        direction = entry.get("Direction", "bullish").lower()

        if status == "entered":
            updated_entries.append(entry)  # Already handled
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

        # Trigger logic based on direction
        triggered = (
            direction == "bullish" and current_price >= trigger_price or
            direction == "bearish" and current_price <= trigger_price
        )

        if triggered:
            log(f"[ENTRY ✅] {symbol} triggered @ {current_price} (Target: {trigger_price})")
            entry["Status"] = "entered"
            # TODO: TradeTracker.mark_trade_entry(entry)  # Optional integration
        else:
            entry["Status"] = "waiting"

        updated_entries.append(entry)

    save_pending_entries(updated_entries)

if __name__ == "__main__":
    check_pending_entries()
