import csv
import os
from datetime import datetime

PREDICTIONS_PATH = "output/logs/predictions.csv"

def log_prediction(symbol, signals, trend, df):
    file_exists = os.path.isfile(PREDICTIONS_PATH)

    # Use the most recent candle
    latest_candle = df.iloc[-1]
    high = round(latest_candle["High"], 2)
    low = round(latest_candle["Low"], 2)
    close = round(latest_candle["Close"], 2)

    # Calculate rolling VWAP at signal time
    try:
        vwap_series = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
        vwap = round(vwap_series.iloc[-1], 2)
    except Exception:
        vwap = ""

    with open(PREDICTIONS_PATH, "a", newline='') as csvfile:
        fieldnames = [
            "Timestamp", "Symbol", "Trend",
            "EMA", "VWAP Signal", "MACD", "RSI", "Volume Spike",
            "Signal High", "Signal Low", "Signal VWAP",
            "Entry Time", "Entry Price",
            "Exit Time", "Exit Price", "Change %", "Outcome"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "Timestamp": datetime.now().isoformat(),
            "Symbol": symbol,
            "Trend": trend,
            "EMA": signals.get("ema_bullish", False),
            "VWAP Signal": signals.get("vwap_above", False),
            "MACD": signals.get("macd_positive", False),
            "RSI": round(signals.get("rsi", 0), 2),
            "Volume Spike": signals.get("volume_spike", False),
            "Signal High": high,
            "Signal Low": low,
            "Signal VWAP": vwap,
            "Entry Time": "",
            "Entry Price": "",
            "Exit Time": "",
            "Exit Price": "",
            "Change %": "",
            "Outcome": ""
        })
