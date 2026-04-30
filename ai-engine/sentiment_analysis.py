import pandas as pd


def analyze_sentiment(reviews: pd.DataFrame) -> dict:
    """Return a simple sentiment analysis stub for the given review dataset."""
    positive = reviews[reviews.apply(lambda row: str(row).lower().count("good") > 0, axis=1)].shape[0]
    negative = reviews[reviews.apply(lambda row: str(row).lower().count("bad") > 0, axis=1)].shape[0]
    total = len(reviews)
    return {
        "total_reviews": int(total),
        "positive_mentions": int(positive),
        "negative_mentions": int(negative),
        "sentiment_summary": "Mostly positive" if positive >= negative else "Mostly negative",
    }
