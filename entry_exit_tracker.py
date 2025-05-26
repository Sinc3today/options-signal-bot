import csv
import os
from datetime import datetime

TRADES_PATH = "output/logs/trades.csv"

# Field headers used consistently
HEADERS = [
    "Symbol", "Entry Time", "Entry Price",
    "Buffer", "Rationale", "Expectation",
    "Signal Source Time", "Trend at Entry",
    "Exit Time", "Exit Price", "Change %", "Outcome", "Notes"
]

def ensure_headers():
    """Ensure the trades file exists with proper headers."""
    os.makedirs(os.path.dirname(TRADES_PATH), exist_ok=True)
    if not os.path.exists(TRADES_PATH):
        with open(TRADES_PATH, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def log_entry(
    symbol,
    entry_price,
    buffer="0%",
    rationale="",
    expectation="",
    signal_time=None,
    trend=""
):
    """Log a new trade entry row."""
    ensure_headers()

    with open(TRADES_PATH, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            symbol,
            datetime.now().isoformat(),  # Entry Time
            entry_price,
            buffer,
            rationale,
            expectation,
            signal_time or "",
            trend,
            "", "", "", "", ""  # Leave exit-related fields blank
        ])

    print(f"[ENTRY ✅] {symbol} @ {entry_price}")

def log_exit(symbol, exit_price, notes="", outcome=None):
    """Mark the most recent open trade for this symbol as exited."""
    rows = []
    updated = False
    exit_time = datetime.now().isoformat()

    try:
        with open(TRADES_PATH, "r", newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for row in reversed(rows):  # Start from most recent
            if row["Symbol"] == symbol and row["Exit Time"] == "":
                try:
                    entry_price = float(row["Entry Price"])
                    change_pct = round(((exit_price - entry_price) / entry_price) * 100, 2)
                except Exception as e:
                    print(f"[EXIT ERROR] Failed to calculate change: {e}")
                    change_pct = ""
                    outcome = "Error"

                row["Exit Time"] = exit_time
                row["Exit Price"] = exit_price
                row["Change %"] = change_pct
                row["Outcome"] = outcome or _default_outcome(change_pct)
                row["Notes"] = notes
                updated = True
                break  # Only update the most recent match

        if not updated:
            print(f"[EXIT ❌] No open trade found for {symbol}")
            return

        with open(TRADES_PATH, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)

        print(f"[EXIT ✅] {symbol} @ {exit_price} | Δ {change_pct}% | Outcome: {row['Outcome']}")

    except Exception as e:
        print(f"[EXIT ❌] Error updating exit for {symbol}: {e}")

def _default_outcome(change_pct):
    """Basic outcome categorization for logging."""
    try:
        change_pct = float(change_pct)
        if change_pct > 0.5:
            return "Win"
        elif change_pct < -0.5:
            return "Loss"
        else:
            return "Neutral"
    except:
        return "Unknown"
