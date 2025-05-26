from entry_exit_tracker import log_entry
from entry_exit_tracker import log_exit

# Example manual trade entry
log_entry(
    symbol="AAPL",
    entry_price=189.12,
    buffer="0.5%",
    rationale="Breakout above high with VWAP + volume support",
    expectation="Target $192 within 2 days. RSI and volume support a breakout.",
    signal_time="2025-05-28T09:45:00",
    trend="Bullish"
)

log_exit(
    symbol="AAPL",
    exit_price=192.25,
    notes="Hit price target. Exiting on strength.",
)