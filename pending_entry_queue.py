# pending_entry_queue.py

import csv
import os
from datetime import datetime

PENDING_PATH = "output/logs/pending_entries.csv"

def ensure_headers():
    if not os.path.exists(PENDING_PATH):
        with open(PENDING_PATH, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Symbol", "Date Logged", "Signal Trend", "Signal Source Time",
                "Signal High", "Signal Low", "VWAP",
                "Entry Condition", "Status", "Entry Time", "Entry Price", "Notes"
            ])

def queue_pending_entry(symbol, trend, signal_time, signal_high, signal_low, vwap, entry_condition, notes=""):
    ensure_headers()

    with open(PENDING_PATH, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            symbol,
            datetime.now().isoformat(),
            trend,
            signal_time,
            round(signal_high, 2),
            round(signal_low, 2),
            round(vwap, 2),
            entry_condition,
            "waiting",  # default status
            "", "", notes
        ])
    print(f"[PENDING ⏳] {symbol} added to pending entry queue.")

def update_pending_status(symbol, new_status, entry_price=None, notes=""):
    rows = []
    updated = False
    with open(PENDING_PATH, "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Symbol"] == symbol and row["Status"] == "waiting" and not updated:
                row["Status"] = new_status
                row["Entry Time"] = datetime.now().isoformat() if new_status == "entered" else ""
                row["Entry Price"] = entry_price if entry_price else ""
                row["Notes"] = notes
                updated = True
            rows.append(row)

    if updated:
        with open(PENDING_PATH, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"[PENDING ✅] {symbol} status updated to {new_status}")
    else:
        print(f"[PENDING ❌] No waiting entry found for {symbol}")
