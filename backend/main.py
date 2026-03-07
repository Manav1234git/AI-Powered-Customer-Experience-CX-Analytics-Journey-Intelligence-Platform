from flask import Flask, jsonify
import pandas as pd
import sys

sys.path.append("../ai-engine")

from sentiment_analysis import analyze_sentiment
from churn_prediction import predict_churn
from recommendation_engine import generate_recommendations
app = Flask(__name__)

reviews = pd.read_csv("../data/customer_reviews.csv")
chats = pd.read_csv("../data/support_chats.csv")
events = pd.read_csv("../data/website_events.csv")

@app.route("/")
def home():
    return {"message": "CX Analytics Backend Running"}

@app.route("/sentiment")
def sentiment():
    result = analyze_sentiment(reviews)
    return jsonify(result)

@app.route("/churn")
def churn():
    result = predict_churn(events)
    return jsonify(result)

@app.route("/recommendations")
def recommendations():
    result = generate_recommendations(reviews, chats, events)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
