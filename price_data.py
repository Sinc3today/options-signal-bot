# price_data.py

import yfinance as yf
import pandas as pd

def get_recent_price_data(symbol, interval="1h", period="5d"):
    try:
        data = yf.download(
            tickers=symbol,
            interval=interval,
            period=period,
            progress=False
        )

        if data.empty:
            print(f"[WARN] No data found for {symbol}")
            return pd.DataFrame()

        # Drop timezone info if present
        if data.index.tz:
            data.index = data.index.tz_localize(None)

        return data

    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {symbol}: {e}")
        return pd.DataFrame()
