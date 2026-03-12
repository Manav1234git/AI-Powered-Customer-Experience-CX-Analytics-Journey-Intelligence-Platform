import pandas as pd

def analyze_reviews():
    df = pd.read_csv("data/customer_reviews.csv")
    
    positive = df[df["rating"] >= 4].shape[0]
    negative = df[df["rating"] <= 2].shape[0]

    return {
        "positive_reviews": positive,
        "negative_reviews": negative
    }