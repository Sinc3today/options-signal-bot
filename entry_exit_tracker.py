import os
import csv
from config import PENDING_ENTRIES_PATH, ENTRY_LOG_PATH

class TradeTracker:

    @staticmethod
    def queue_pending_entry(symbol, trend, signal_time, signal_high, signal_low, vwap, entry_condition, notes=""):
        os.makedirs(os.path.dirname(PENDING_ENTRIES_PATH), exist_ok=True)
        headers = ["Symbol", "Trend", "Signal Source Time", "High", "Low", "VWAP", "Entry Condition", "Notes", "Status", "Trigger Price", "Direction"]
        row = {
            "Symbol": symbol,
            "Trend": trend,
            "Signal Source Time": signal_time,
            "High": signal_high,
            "Low": signal_low,
            "VWAP": vwap,
            "Entry Condition": entry_condition,
            "Notes": notes,
            "Status": "waiting",
            "Trigger Price": 0.0,
            "Direction": trend.lower()
        }
        file_exists = os.path.exists(PENDING_ENTRIES_PATH)
        with open(PENDING_ENTRIES_PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    @staticmethod
    def mark_trade_entry(entry_data):
        os.makedirs(os.path.dirname(ENTRY_LOG_PATH), exist_ok=True)
        file_exists = os.path.exists(ENTRY_LOG_PATH)
        with open(ENTRY_LOG_PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=entry_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(entry_data)
