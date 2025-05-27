# 📊 Project Module Overview & Optimization Plan

| Module | Purpose | To Improve |
|--------|---------|------------|
| `main.py` | Main trading loop. Pulls price data, analyzes signals, queues predictions. | Split main() into smaller functions; add --dry-run mode; handle yfinance errors |
| `price_data.py` | Pulls recent price data from yfinance. | Add get_current_price(); batch fetch; add retry logic |
| `signals.py` | Computes technical indicators using `ta`. | Group indicators into one pass; modularize logic |
| `predictor.py` | Scores signal outputs as bullish/bearish/neutral. | Allow weighting rules; add confidence score |
| `strategy_engine.py` | Checks if signal meets trade entry conditions. | Externalize thresholds; support per-symbol logic |
| `prediction_logger.py` | Logs scored predictions to CSV. | Switch to pandas for appending; add session ID |
| `discord_alert.py` | Sends Discord alerts using bot token. | Use template-based formatting; embed alerts |
| `pending_entry_queue.py` | Queues valid trades to pending_entries.csv. | Add expiration field; refactor into class |
| `evaluate_pending_entries.py` | Confirms triggered entries from queue. | Batch pull prices; alert on entry; prevent reprocessing |
| `entry_exit_tracker.py` | Logs actual trade entries and exits. | Build exit logic; calculate P&L; use SQLite |
| `cleanup_bot.py` | Deletes old Discord messages. | Add permission checks; command logging |
| `signal_bot_responder.py` | Responds to user commands/emoji in Discord. | Summarize signal details; enforce bot token rules |
| `test_trade_entry.py` | Manual entry/exit testing stub. | Convert to pytest-based unit test suite |
| `config.py` | Holds static constants and paths. | Centralize all tunable values and thresholds |