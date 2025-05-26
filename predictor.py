# predictor.py

def score_signals(signals: dict) -> str:
    if "error" in signals:
        return "Neutral"

    bullish_score = 0
    bearish_score = 0

    if signals.get("ema_bullish"): bullish_score += 1
    if signals.get("ema_bearish"): bearish_score -= 1

    if signals.get("vwap_above"): bullish_score += 1
    if signals.get("vwap_below"): bearish_score -= 1

    if signals.get("macd_positive"): bullish_score += 1
    if signals.get("macd_negative"): bearish_score -= 1

    if signals.get("rsi_bullish"): bullish_score += 1
    if signals.get("rsi_bearish"): bearish_score -= 1

    if signals.get("volume_spike"): bullish_score += 1

    # Final decision
    if bullish_score >= 3:
        return "Bullish"
    elif bearish_score <= -2:
        return "Bearish"
    else:
        return "Neutral"
