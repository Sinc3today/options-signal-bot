# config.py

# Bot Tokens
# Cleanup Bot = MTM3NjQxNzU4NzE5NzM4Mjc0Nw.G6nfUv.ZjySBPH9JuTedhotDWcWPUZojA_FOao-UEmzLg
# Alert Bot = MTM3NDEyMzAzMjQxMDU4NzI0OA.GepmHS.32j1zXzlGMS_2bskSP8R1k8Bu-ShEUGF8x1FXQ
# Market timing
MARKET_OPEN_TIME = "09:30"
START_ANALYSIS_TIME = "09:35"
END_ANALYSIS_TIME = "10:00"
INTERVAL_MINUTES = 5

# Paths
STOCK_LIST_PATH = "data/stocks.csv"
LOG_PATH = "output/logs/"

# Data Fetching Settings
DEFAULT_INTERVAL = "5m"         # or "1h", "15m", etc.
DEFAULT_PERIOD = "1d"           # or "5d", "7d" for extended lookback

# Long-Term Trend Evaluation Settings
ENABLE_LONG_TERM_TREND_CONFIRMATION = True

# Used to evaluate higher timeframe trend (to confirm or reject entry)
LONG_TERM_INTERVAL = "1h"    # Options: "1h", "1d"
LONG_TERM_PERIOD = "7d"      # Options: "7d", "1mo", etc.

# Optionally require exact match
REQUIRE_TREND_MATCH = True  # True = entry only if short-term and long-term agree

# Entry Signal Strategy Configuration
ENTRY_RULES = {
    "Bullish": [
        "ema_bullish",
        "vwap_above",
        "macd_positive",
        "rsi_bullish",
        "volume_spike"
    ],
    "Bearish": [
        "ema_bearish",
        "vwap_below",
        "macd_negative",
        "rsi_bearish",
        "volume_spike"
    ]
}

# Entry logic mode
USE_SCORING_MODE = True  # True = percent match (e.g., 80% of rules must match)
MIN_MATCH_THRESHOLD = 0.8  # Used for scoring mode (e.g. 4 out of 5)

# If not using scoring, this becomes a fixed minimum match count
# e.g., 4 means at least 4 signals must match


