import os
import datetime
import argparse
import pandas as pd
import re

# Import config constants
from config import DEFAULT_INTERVAL, DEFAULT_PERIOD, STOCK_LIST_PATH
from price_data import get_recent_price_data
from signals import analyze_signals
from predictor import score_signals
from prediction_logger import log_prediction
from discord_alert import send_discord_alert, run_discord_bot
from strategy_engine import evaluate_entry_conditions
from logger import log
from entry_exit_tracker import TradeTracker

# Clean out stale or expired pending entries
def clean_old_pending_entries(days_old=2):
    path = "output/logs/pending_entries.csv"
    if not os.path.exists(path):
        return
    try:
        df = pd.read_csv(path)
        if "Signal Source Time" not in df.columns or "Status" not in df.columns:
            return
        df["Signal Source Time"] = pd.to_datetime(df["Signal Source Time"], errors='coerce')
        now = pd.Timestamp.now()
        mask = (df["Status"] == "waiting") & ((now - df["Signal Source Time"]).dt.days >= days_old)
        removed = df[mask]
        df = df[~mask]
        df.to_csv(path, index=False)
        if not removed.empty:
            log(f"[CLEANUP] Removed {len(removed)} stale pending entries older than {days_old} days.")
    except Exception as e:
        log(f"[ERROR] Failed to clean old pending entries: {e}")

# Clean up any malformed entries in the pending queue
if os.path.exists("output/logs/pending_entries.csv"):
    df = pd.read_csv("output/logs/pending_entries.csv")
    cleaned = df[~df["Entry Condition"].str.contains("Ticker", na=False)]
    cleaned.to_csv("output/logs/pending_entries.csv", index=False)
    print("Cleaned malformed entries from pending_entries.csv.")

# Deprecated — now handled by logger.py
# Kept in case you want to re-integrate emoji stripping elsewhere
LOG_PATH = "output/logs/tasklog.txt"

def strip_emoji(text):
    emoji_pattern = re.compile("[" "\U0001F600-\U0001F64F"
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

# Parse CLI args or fallback to defaults
def parse_args():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--interval', type=str, default=DEFAULT_INTERVAL)
        parser.add_argument('--period', type=str, default=DEFAULT_PERIOD)
        parser.add_argument('--force', action='store_true')  # Forces run even outside market hours
        args = parser.parse_args()
        log(f"Args parsed: interval={args.interval}, period={args.period}, force={args.force}")
        return args
    except Exception as e:
        log(f"[ERROR] parse_args() failed: {e}")
        # Fallback defaults
        class Args:
            interval = DEFAULT_INTERVAL
            period = DEFAULT_PERIOD
            force = True
        return Args()

# Load symbols from CSV
def load_stock_list():
    try:
        log(f"Loading stock list from: {STOCK_LIST_PATH}")
        df = pd.read_csv(STOCK_LIST_PATH)
        stock_list = df['Symbol'].dropna().tolist()
        log(f"Stock list loaded: {stock_list}")
        return stock_list
    except Exception as e:
        log(f"[ERROR] Failed to load stock list: {e}")
        return []

# Prevent duplicate entries for the same trigger price
def is_already_queued(symbol, trigger_price):
    path = "output/logs/pending_entries.csv"
    if not os.path.exists(path):
        return False
    df = pd.read_csv(path)
    return any((df["Symbol"] == symbol) & (df["Status"] == "waiting") & (df["Entry Condition"].str.contains(f"{trigger_price}")))

# MAIN LOGIC
def main():
    log("main.py started successfully.")
    clean_old_pending_entries(days_old=2)
    args = parse_args()

    now = datetime.datetime.now()
    if not args.force and not (datetime.time(9, 35) <= now.time() <= datetime.time(10, 0)):
        log("Outside analysis time window. Exiting.")
        return

    log("Signal bot started")
    stock_list = load_stock_list()
    if not stock_list:
        log("No stocks to analyze. Exiting.")
        return

    for symbol in stock_list:
        try:
            log(f"Fetching data for {symbol}")
            df = get_recent_price_data(symbol, interval=args.interval, period=args.period)
            if df.empty:
                log(f"No data retrieved for {symbol}")
                continue

            # Save fetched data for review/debug
            df.to_csv(f"data/history/{symbol}_latest.csv")

            # Generate signals and trend score
            signals = analyze_signals(df)
            trend = score_signals(signals)

            # Long-term trend filter (optional)
            from config import (
                ENABLE_LONG_TERM_TREND_CONFIRMATION,
                LONG_TERM_INTERVAL,
                LONG_TERM_PERIOD,
                REQUIRE_TREND_MATCH
            )

            if ENABLE_LONG_TERM_TREND_CONFIRMATION:
                df_long = get_recent_price_data(symbol, interval=LONG_TERM_INTERVAL, period=LONG_TERM_PERIOD)
                if df_long.empty:
                    log(f"[LONG TREND] Skipped {symbol}: No long-term data.")
                    continue
                long_signals = analyze_signals(df_long)
                long_trend = score_signals(long_signals)

                if REQUIRE_TREND_MATCH and trend != long_trend:
                    log(f"[FILTER ❌] {symbol}: {trend} trend rejected by long-term {long_trend}")
                    continue

            # Log trend and indicators to prediction file
            log_prediction(symbol, signals, trend, df)

            # Decide if entry condition is valid
            entry_decision = evaluate_entry_conditions(symbol, df, signals, trend)
            if not entry_decision:
                continue

            # Calculate entry signal values
            signal_high = float(df["High"].iloc[-1].item())
            signal_low = float(df["Low"].iloc[-1].item())
            vwap = round((df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum(), 2).iloc[-1].item()

            if trend == "Bullish":
                trigger_price = round(signal_high * 1.005, 2)
                entry_condition = f"Break above {trigger_price} (0.5% buffer)"
            elif trend == "Bearish":
                trigger_price = round(signal_low * 0.995, 2)
                entry_condition = f"Break below {trigger_price} (0.5% buffer)"
            else:
                continue

            # Prevent duplicate queues
            if is_already_queued(symbol, trigger_price):
                log(f"[SKIP] {symbol} already queued for {trigger_price}")
                continue

            # Save pending entry for later evaluation
            TradeTracker.queue_pending_entry(
                symbol=symbol,
                trend=trend,
                signal_time=datetime.datetime.now().isoformat(),
                signal_high=signal_high,
                signal_low=signal_low,
                vwap=vwap,
                entry_condition=entry_condition,
                notes="Auto-queued by strategy engine"
            )
            log(f"[PENDING] {symbol} queued for confirmation at {trigger_price}")

            # Send alert to Discord
            send_discord_alert(symbol, trend, signals)
            log(f"[ALERT ✅] {symbol} - {trend} alert sent.")

        except Exception as e:
            log(f"[ERROR] Failed to process {symbol}: {e}")

    # Launch Discord bot responder (emoji handler, etc.)
    try:
        run_discord_bot()
    except Exception as e:
        log(f"[ERROR] Failed to run Discord bot: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"[FATAL] main.py crashed: {e}")
