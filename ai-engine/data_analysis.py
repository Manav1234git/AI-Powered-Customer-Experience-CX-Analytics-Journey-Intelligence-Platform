import pandas as pd

def analyze_reviews():
    df = pd.read_csv("data/customer_reviews.csv")
    
    positive = df[df["rating"] >= 4].shape[0]
    negative = df[df["rating"] <= 2].shape[0]

    return {
        "positive_reviews": positive,
        "negative_reviews": negative
    }
    import pandas as pd

def analyze_customer_reviews():
    df = pd.read_csv("data/customer_reviews.csv")

    avg_rating = df["rating"].mean()
    total_reviews = len(df)

    return {
        "average_rating": avg_rating,
        "total_reviews": total_reviews
    }

    def get_dataset_summary():
    import pandas as pd
    df = pd.read_csv("data/customer_reviews.csv")

    return {
        "rows": df.shape[0],
        "columns": df.shape[1]
    }