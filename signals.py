# signals.py

import pandas as pd
import ta

def analyze_signals(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 30:
        return {"error": "Not enough data"}

    result = {}

    # Ensure 1D Series
    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    volume = df["Volume"].squeeze()

    # 1. EMA Crossover
    df["ema9"] = ta.trend.ema_indicator(close, window=9)
    df["ema21"] = ta.trend.ema_indicator(close, window=21)
    result["ema_bullish"] = df["ema9"].iloc[-1] > df["ema21"].iloc[-1]
    result["ema_bearish"] = df["ema9"].iloc[-1] < df["ema21"].iloc[-1]

    # 2. VWAP
    df["vwap"] = ta.volume.volume_weighted_average_price(high, low, close, volume)
    result["vwap_above"] = close.iloc[-1] > df["vwap"].iloc[-1]
    result["vwap_below"] = close.iloc[-1] < df["vwap"].iloc[-1]

    # 3. MACD Histogram
    macd_hist = ta.trend.macd_diff(close)
    result["macd_positive"] = macd_hist.iloc[-1] > 0
    result["macd_negative"] = macd_hist.iloc[-1] < 0

    # 4. RSI
    rsi = ta.momentum.rsi(close)
    result["rsi"] = rsi.iloc[-1]
    result["rsi_bullish"] = rsi.iloc[-1] > 50
    result["rsi_bearish"] = rsi.iloc[-1] < 50

    # 5. Volume Spike
    avg_vol = volume.rolling(window=20).mean()
    result["volume_spike"] = volume.iloc[-1] > avg_vol.iloc[-1] * 1.5

    return result
