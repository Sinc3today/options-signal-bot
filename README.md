# 🧠 Options Signal Bot

An automated Python bot that analyzes early morning price action across selected stocks and sends entry signals to Discord and Google Sheets. Designed to detect bullish/bearish patterns using technical indicators and track manual or auto entries for journaling.

## 📈 Features
- Monitors EMA crossover, VWAP, MACD, RSI, and volume divergence
- Predicts price direction and logs confidence scores
- Runs every 5 minutes after market open until 10:00 AM
- Logs to predictions.csv and system logs
- Discord alerts + `!explain` reaction support
- Manual and auto trade tracking via `entry_exit_tracker.py`
- Entry queue evaluation with trigger and expiration logic

## 🚀 Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/Sinc3today/options-signal-bot.git
   cd options-signal-bot
