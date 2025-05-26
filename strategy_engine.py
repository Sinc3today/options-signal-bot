# strategy_engine.py

from config import ENTRY_RULES, MIN_MATCH_THRESHOLD, USE_SCORING_MODE

def evaluate_entry_conditions(symbol, df, signals, trend):
    rules = ENTRY_RULES.get(trend)
    if not rules:
        return None  # No rules defined for this trend

    # Count how many signals match the required rule set
    matches = sum(1 for rule in rules if signals.get(rule))

    # Optionally return score (even if entry is not triggered)
    signal_score = matches / len(rules)

    if USE_SCORING_MODE:
        if signal_score >= MIN_MATCH_THRESHOLD:
            return {
                "price": df["Close"].iloc[-1],
                "buffer": "0.5%",
                "rationale": f"{trend} setup based on signal score {signal_score:.2f}",
                "expectation": f"{trend} trend continuation"
            }
    else:
        if matches >= MIN_MATCH_THRESHOLD:
            return {
                "price": df["Close"].iloc[-1],
                "buffer": "0.5%",
                "rationale": f"{trend} setup met with {matches} signal matches",
                "expectation": f"{trend} trend continuation"
            }

    return None
