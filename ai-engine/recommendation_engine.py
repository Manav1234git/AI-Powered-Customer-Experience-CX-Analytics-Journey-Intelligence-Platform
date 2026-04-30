import pandas as pd


def generate_recommendations(reviews: pd.DataFrame, chats: pd.DataFrame, events: pd.DataFrame) -> dict:
    """Return a simple recommendations stub based on available datasets."""
    return {
        "recommendations": [
            "Review customer feedback trends weekly",
            "Follow up on high churn-risk accounts",
            "Expand support resources for repeat issues",
        ],
        "review_count": int(len(reviews)),
        "chat_count": int(len(chats)),
        "event_count": int(len(events)),
    }
