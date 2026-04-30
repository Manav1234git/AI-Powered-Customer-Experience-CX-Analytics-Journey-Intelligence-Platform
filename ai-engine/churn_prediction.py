import pandas as pd


def predict_churn(events: pd.DataFrame) -> dict:
    """Return a simple churn prediction stub based on event counts."""
    total = len(events)
    churn_score = 0.1 if total > 0 else 0.0
    return {
        "total_events": int(total),
        "churn_probability": churn_score,
        "risk_level": "low" if churn_score < 0.3 else "high",
    }
