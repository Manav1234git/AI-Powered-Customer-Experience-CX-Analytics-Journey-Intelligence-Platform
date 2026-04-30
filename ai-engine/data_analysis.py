import pandas as pd


def analyze_reviews():
    df = pd.read_csv("data/customer_reviews.csv")

    positive = df[df["rating"] >= 4].shape[0]
    negative = df[df["rating"] <= 2].shape[0]

    return {
        "positive_reviews": positive,
        "negative_reviews": negative
    }


def analyze_customer_reviews():
    df = pd.read_csv("data/customer_reviews.csv")

    avg_rating = df["rating"].mean()
    total_reviews = len(df)

    return {
        "average_rating": avg_rating,
        "total_reviews": total_reviews
    }


def get_dataset_summary():
    df = pd.read_csv("data/customer_reviews.csv")

    return {
        "rows": df.shape[0],
        "columns": df.shape[1]
    }

def get_sentiment_ratio():
    df = pd.read_csv("data/customer_reviews.csv")

    positive = (df["rating"] >= 4).sum()
    total = len(df)

    return {
        "positive_ratio": positive / total
    }

def category_analysis():
    df = pd.read_csv("data/customer_reviews.csv")
    return df.groupby("product_category")["rating"].mean().to_dict()

def get_top_category():
    df = pd.read_csv("data/customer_reviews.csv")
    return df.groupby("product_category")["rating"].mean().idxmax()

def analyze_support_chats():
    df = pd.read_csv("data/support_chats.csv")

    avg_duration = df["duration_minutes"].mean()
    resolved = (df["resolution_status"] == "Resolved").sum()

    return {
        "avg_duration": avg_duration,
        "resolved_cases": resolved
    }

def analyze_events():
    df = pd.read_csv("data/website_events.csv")

    return df["event_type"].value_counts().to_dict()