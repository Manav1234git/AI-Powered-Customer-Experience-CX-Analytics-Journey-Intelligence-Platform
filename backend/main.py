import math
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import io

app = FastAPI(title="CX Analytics API")

# Allow CORS for localhost:3000 and 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN MEMORY DATA ---

# Sample customers
customers_db = [
    {"customer_id": "C001", "name": "Alice Smith", "ticket_count": 2, "inactive_days": 10},
    {"customer_id": "C002", "name": "Bob Jones", "ticket_count": 5, "inactive_days": 40},
    {"customer_id": "C003", "name": "Charlie Brown", "ticket_count": 0, "inactive_days": 5},
    {"customer_id": "C004", "name": "Diana Prince", "ticket_count": 1, "inactive_days": 20},
    {"customer_id": "C005", "name": "Evan Wright", "ticket_count": 8, "inactive_days": 60},
    {"customer_id": "C006", "name": "Fiona Gallagher", "ticket_count": 3, "inactive_days": 15},
    {"customer_id": "C007", "name": "George Miller", "ticket_count": 0, "inactive_days": 2},
    {"customer_id": "C008", "name": "Hannah Abbott", "ticket_count": 4, "inactive_days": 35},
    {"customer_id": "C009", "name": "Ian Malcolm", "ticket_count": 6, "inactive_days": 45},
    {"customer_id": "C010", "name": "Julia Child", "ticket_count": 1, "inactive_days": 8},
]

# Sample reviews
reviews_db = [
    {"id": 1, "customer_id": "C001", "name": "Alice Smith", "text": "Great service, very happy with the product!", "rating": 5, "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.4},
    {"id": 2, "customer_id": "C002", "name": "Bob Jones", "text": "Terrible experience, the worst support ever.", "rating": 1, "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.6},
    {"id": 3, "customer_id": "C003", "name": "Charlie Brown", "text": "Good value for money.", "rating": 4, "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.2},
    {"id": 4, "customer_id": "C004", "name": "Diana Prince", "text": "It was okay, nothing special.", "rating": 3, "date": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"), "sentiment_label": "Neutral", "sentiment_score": 0.0},
    {"id": 5, "customer_id": "C005", "name": "Evan Wright", "text": "Awful platform, so broken.", "rating": 1, "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.5},
    {"id": 6, "customer_id": "C006", "name": "Fiona Gallagher", "text": "Excellent tools, amazing team.", "rating": 5, "date": (datetime.now() - timedelta(days=18)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.5},
    {"id": 7, "customer_id": "C007", "name": "George Miller", "text": "Awesome features, love it.", "rating": 5, "date": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.6},
    {"id": 8, "customer_id": "C008", "name": "Hannah Abbott", "text": "Very poor UI, bad navigation.", "rating": 2, "date": (datetime.now() - timedelta(days=22)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.4},
    {"id": 9, "customer_id": "C009", "name": "Ian Malcolm", "text": "Hate the new update. Horrible.", "rating": 1, "date": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.8},
    {"id": 10, "customer_id": "C010", "name": "Julia Child", "text": "Satisfied with the purchase.", "rating": 4, "date": (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.3},
    {"id": 11, "customer_id": "C001", "name": "Alice Smith", "text": "Really amazing updates!", "rating": 5, "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.5},
    {"id": 12, "customer_id": "C002", "name": "Bob Jones", "text": "Still bad, very slow.", "rating": 2, "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.4},
    {"id": 13, "customer_id": "C003", "name": "Charlie Brown", "text": "Working well for me.", "rating": 4, "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), "sentiment_label": "Neutral", "sentiment_score": 0.0},
    {"id": 14, "customer_id": "C006", "name": "Fiona Gallagher", "text": "Great job guys.", "rating": 5, "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.3},
    {"id": 15, "customer_id": "C008", "name": "Hannah Abbott", "text": "Not satisfied yet.", "rating": 2, "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.2},
]

# Sample journey touchpoints
journeys_db = {
    "C001": [
        {"date": "2023-10-01", "channel": "email", "sentiment": "Neutral", "resolved": "Y"},
        {"date": "2023-10-15", "channel": "chat", "sentiment": "Positive", "resolved": "Y"}
    ],
    "C002": [
        {"date": "2023-09-20", "channel": "phone", "sentiment": "Negative", "resolved": "N"},
        {"date": "2023-09-25", "channel": "chat", "sentiment": "Negative", "resolved": "N"},
        {"date": "2023-10-05", "channel": "email", "sentiment": "Negative", "resolved": "N"}
    ]
}

# Admin API Key
app_config = {
    "api_key": ""
}

# --- HELPER FUNCTIONS ---

def calculate_sentiment(text: str):
    positive_words = ["great", "excellent", "love", "happy", "satisfied", "amazing", "good", "awesome"]
    negative_words = ["bad", "terrible", "horrible", "worst", "hate", "poor", "awful", "disappointed", "slow", "broken"]
    
    words = text.lower().split()
    if not words:
        return 0.0, "Neutral"
        
    pos_count = sum(1 for word in words if any(pw in word for pw in positive_words))
    neg_count = sum(1 for word in words if any(nw in word for nw in negative_words))
    
    score = (pos_count - neg_count) / len(words)
    score = max(-1.0, min(1.0, score)) # clamp to [-1, 1]
    
    if score > 0.1:
        label = "Positive"
    elif score < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
        
    return score, label

def get_customer_avg_sentiment(customer_id: str):
    customer_reviews = [r for r in reviews_db if r["customer_id"] == customer_id]
    if not customer_reviews:
        return 0.0
    return sum(r["sentiment_score"] for r in customer_reviews) / len(customer_reviews)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def calculate_churn_risk(customer):
    avg_sentiment = get_customer_avg_sentiment(customer["customer_id"])
    x = 0.3 * customer["ticket_count"] + 0.4 * (customer["inactive_days"] / 30) - 0.5 * avg_sentiment
    prob = sigmoid(x)
    
    if prob < 0.3:
        level = "Low"
    elif prob <= 0.6:
        level = "Medium"
    else:
        level = "High"
        
    return {"prob": prob, "level": level, "avg_sentiment": avg_sentiment}

# --- MODELS ---

class ReviewInput(BaseModel):
    customer_id: str
    name: str
    text: str
    rating: int
    date: str

class AIQuery(BaseModel):
    question: str

class APIKeyInput(BaseModel):
    api_key: str

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "CX Analytics API is running"}

@app.post("/submit-review")
def submit_review(review: ReviewInput):
    score, label = calculate_sentiment(review.text)
    new_review = {
        "id": len(reviews_db) + 1,
        "customer_id": review.customer_id,
        "name": review.name,
        "text": review.text,
        "rating": review.rating,
        "date": review.date,
        "sentiment_label": label,
        "sentiment_score": score
    }
    reviews_db.append(new_review)
    return {"status": "success", "review": new_review}

@app.get("/reviews")
def get_reviews():
    # Return mostly recent reviews first
    return sorted(reviews_db, key=lambda x: x["id"], reverse=True)

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(status_code=400, detail="Only CSV or JSON files are supported.")
    
    content = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_json(io.StringIO(content.decode('utf-8')))
        
        # Simple analysis
        stats = {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
        return {"status": "success", "filename": file.filename, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-data")
def analyze_data():
    # Simulated analysis response
    return {
        "status": "success",
        "results": {
            "total_analyzed": 1500,
            "sentiment_distribution": {"Positive": 60, "Neutral": 25, "Negative": 15},
            "top_topics": ["Pricing", "Customer Support", "Performance", "UI/UX"]
        }
    }

@app.get("/insights")
def get_insights():
    total_customers = len(customers_db)
    avg_sentiment = sum(r["sentiment_score"] for r in reviews_db) / len(reviews_db) if reviews_db else 0.0
    
    all_churns = [calculate_churn_risk(c)["prob"] for c in customers_db]
    avg_churn_risk = sum(all_churns) / len(all_churns) if all_churns else 0.0
    
    # Calculate NPS: (Promoters (4-5) - Detractors (1-2)) / Total * 100
    if reviews_db:
        promoters = sum(1 for r in reviews_db if r["rating"] >= 4)
        detractors = sum(1 for r in reviews_db if r["rating"] <= 2)
        nps = ((promoters - detractors) / len(reviews_db)) * 100
    else:
        nps = 0.0

    return {
        "total_customers": total_customers,
        "avg_sentiment": round(avg_sentiment, 2),
        "avg_churn_risk": round(avg_churn_risk * 100, 1),
        "nps_score": round(nps, 1)
    }

@app.get("/sentiment-trend")
def get_sentiment_trend():
    # Return last 30 days dummy data mixed with real
    # For simplicity, returning a predefined trend combined with actual data grouped by date
    df = pd.DataFrame(reviews_db)
    if not df.empty:
        trend = df.groupby('date')['sentiment_score'].mean().reset_index()
        trend = trend.sort_values('date')
        return trend.to_dict(orient='records')
    return []

@app.get("/churn-risk")
def get_churn_risk():
    results = []
    for c in customers_db:
        risk_info = calculate_churn_risk(c)
        results.append({
            "customer_id": c["customer_id"],
            "name": c["name"],
            "sentiment_score": round(risk_info["avg_sentiment"], 2),
            "ticket_count": c["ticket_count"],
            "inactive_days": c["inactive_days"],
            "churn_risk_pct": round(risk_info["prob"] * 100, 1),
            "risk_level": risk_info["level"]
        })
    return results

@app.post("/query-ai")
def query_ai(query: AIQuery):
    q = query.question.lower()
    # Simulated AI responses
    if "risk" in q or "churn" in q:
        risky = [c["name"] for c in customers_db if calculate_churn_risk(c)["level"] == "High"]
        ans = f"Based on our data, the customers most at risk of churning are: {', '.join(risky)}." if risky else "Currently, no customers are at a high risk of churning."
    elif "complaint" in q or "negative" in q:
        ans = "The top complaints this week revolve around 'slow performance' and 'poor navigation' in the UI."
    elif "sentiment" in q:
        avg = sum(r["sentiment_score"] for r in reviews_db) / len(reviews_db) if reviews_db else 0
        ans = f"The overall average sentiment is {round(avg, 2)}. People are generally positive, but there are a few detractors."
    else:
        ans = "I'm your AI Copilot. I can analyze the CX data for you. Try asking about 'churn risk', 'top complaints', or 'sentiment'."
        
    return {"answer": ans}

@app.get("/journey/{customer_id}")
def get_journey(customer_id: str):
    return journeys_db.get(customer_id, [
        {"date": "2023-01-01", "channel": "system", "sentiment": "Neutral", "resolved": "Y", "note": "Account created"}
    ])

@app.post("/admin/api-key")
def update_api_key(key_input: APIKeyInput):
    app_config["api_key"] = key_input.api_key
    return {"status": "success", "message": "API key updated successfully"}
