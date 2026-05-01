import math
import io
import json
import pickle
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import google.generativeai as genai
import bcrypt
from jose import JWTError, jwt

app = FastAPI(title="CX Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MONGODB SETUP ---
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["cx_analytics"]

# Collections
users_col = db["users"]
customers_col = db["customers"]
reviews_col = db["reviews"]
journeys_col = db["journeys"]

# --- AUTH SETUP ---
SECRET_KEY = "super-secret-key-for-pilot-presentation-only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password)

def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- SETUP AI AND ML MODELS ---
GEMINI_API_KEY = "AIzaSyCnquOqw-cguYV-N8PW5yhX3pkPQyZRy7M"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

try:
    with open('churn_model.pkl', 'rb') as f:
        ml_data = pickle.load(f)
        churn_model = ml_data['model']
        scaler = ml_data['scaler']
except Exception as e:
    print("WARNING: Could not load churn_model.pkl. Run train_model.py first.")
    churn_model = None
    scaler = None

# --- POPULATE DB ON STARTUP (IF EMPTY) ---
def init_db():
    # Check for Admin user
    if users_col.count_documents({"email": "admin@cx.com"}) == 0:
        hashed_pwd = get_password_hash("admin123")
        users_col.insert_one({"email": "admin@cx.com", "hashed_password": hashed_pwd, "full_name": "System Admin", "is_active": True})

    # Check for customers
    if customers_col.count_documents({}) > 0:
        return
    
    customers_data = [
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
    customers_col.insert_many(customers_data)
        
    reviews_data = [
        {"customer_id": "C001", "name": "Alice Smith", "text": "Great service, very happy with the product!", "rating": 5, "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.8},
        {"customer_id": "C002", "name": "Bob Jones", "text": "Terrible experience, the worst support ever.", "rating": 1, "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.9},
        {"customer_id": "C003", "name": "Charlie Brown", "text": "Good value for money.", "rating": 4, "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.5},
        {"customer_id": "C004", "name": "Diana Prince", "text": "It was okay, nothing special.", "rating": 3, "date": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"), "sentiment_label": "Neutral", "sentiment_score": 0.0},
        {"customer_id": "C005", "name": "Evan Wright", "text": "Awful platform, so broken.", "rating": 1, "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.8},
        {"customer_id": "C006", "name": "Fiona Gallagher", "text": "Excellent tools, amazing team.", "rating": 5, "date": (datetime.now() - timedelta(days=18)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.9},
    ]
    reviews_col.insert_many(reviews_data)
        
    journeys_data = [
        {"customer_id": "C001", "date": "2023-10-01", "channel": "email", "sentiment": "Neutral", "resolved": "Y", "note": ""},
        {"customer_id": "C001", "date": "2023-10-15", "channel": "chat", "sentiment": "Positive", "resolved": "Y", "note": ""},
        {"customer_id": "C002", "date": "2023-09-20", "channel": "phone", "sentiment": "Negative", "resolved": "N", "note": ""},
    ]
    journeys_col.insert_many(journeys_data)

# --- HELPER FUNCTIONS ---
def calculate_sentiment(text: str):
    prompt = f"""
    Analyze the following customer feedback. 
    1. Determine a sentiment score between -1.0 (extremely negative) and 1.0 (extremely positive).
    2. Provide a single word label: Positive, Neutral, or Negative.
    
    Format your response EXACTLY as a JSON object: {{"score": float, "label": "string"}}
    Do not include markdown or other text.
    
    Feedback: "{text}"
    """
    try:
        response = gemini_model.generate_content(prompt)
        text_resp = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_resp)
        return float(data.get("score", 0.0)), data.get("label", "Neutral")
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return 0.0, "Neutral"

def calc_churn_for_db(customer, avg_sentiment):
    if churn_model and scaler:
        features = pd.DataFrame([{'ticket_count': customer.get('ticket_count', 0), 'inactive_days': customer.get('inactive_days', 0), 'avg_sentiment': avg_sentiment}])
        X_scaled = scaler.transform(features)
        prob = churn_model.predict_proba(X_scaled)[0][1]
    else:
        x = 0.3 * customer.get('ticket_count', 0) + 0.4 * (customer.get('inactive_days', 0) / 30) - 0.5 * avg_sentiment
        prob = 1 / (1 + math.exp(-x))
    
    if prob < 0.3: level = "Low"
    elif prob <= 0.6: level = "Medium"
    else: level = "High"
    return {"prob": prob, "level": level, "avg_sentiment": avg_sentiment}

# --- Pydantic Models ---
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

class ReviewInput(BaseModel):
    customer_id: str
    name: str
    text: str
    rating: int
    date: str

class AIQuery(BaseModel):
    question: str

# --- ENDPOINTS ---
@app.on_event("startup")
def on_startup():
    init_db()

# AUTH ENDPOINTS
@app.post("/api/register")
def register_user(user: UserCreate):
    if users_col.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = {"email": user.email, "hashed_password": hashed_password, "full_name": user.full_name, "is_active": True}
    users_col.insert_one(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": user.email, "name": user.full_name}}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_col.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["email"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": user["email"], "name": user.get("full_name", "")}}

# PROTECTED DEPENDENCY
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_col.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

@app.get("/api/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "name": current_user.get("full_name", "")}


@app.post("/submit-review")
def submit_review(review: ReviewInput):
    score, label = calculate_sentiment(review.text)
    new_rev = {
        "customer_id": review.customer_id, "name": review.name, "text": review.text, "rating": review.rating,
        "date": review.date, "sentiment_label": label, "sentiment_score": score
    }
    result = reviews_col.insert_one(new_rev)
    new_rev["_id"] = str(result.inserted_id)
    
    if not customers_col.find_one({"customer_id": review.customer_id}):
        customers_col.insert_one({"customer_id": review.customer_id, "name": review.name, "ticket_count": 0, "inactive_days": 0})
    return {"status": "success", "review": new_rev}

@app.get("/reviews")
def get_reviews():
    reviews = list(reviews_col.find().sort("_id", -1))
    for r in reviews:
        r["id"] = str(r.pop("_id"))
    return reviews

@app.get("/insights")
def get_insights():
    customers = list(customers_col.find())
    reviews = list(reviews_col.find())
    total_customers = len(customers)
    avg_sentiment = sum(r.get("sentiment_score", 0) for r in reviews) / len(reviews) if reviews else 0.0
    
    all_churns = []
    for c in customers:
        c_revs = [r for r in reviews if r.get("customer_id") == c.get("customer_id")]
        c_avg = sum(r.get("sentiment_score", 0) for r in c_revs) / len(c_revs) if c_revs else 0.0
        all_churns.append(calc_churn_for_db(c, c_avg)["prob"])
    avg_churn_risk = sum(all_churns) / len(all_churns) if all_churns else 0.0
    
    nps = 0.0
    if reviews:
        promoters = sum(1 for r in reviews if r.get("rating", 0) >= 4)
        detractors = sum(1 for r in reviews if r.get("rating", 0) <= 2)
        nps = ((promoters - detractors) / len(reviews)) * 100

    return {
        "total_customers": total_customers,
        "avg_sentiment": round(avg_sentiment, 2),
        "avg_churn_risk": round(avg_churn_risk * 100, 1),
        "nps_score": round(nps, 1)
    }

@app.get("/sentiment-trend")
def get_sentiment_trend():
    reviews = list(reviews_col.find())
    if not reviews: return []
    df = pd.DataFrame([{ "date": r.get("date"), "sentiment_score": r.get("sentiment_score", 0) } for r in reviews])
    trend = df.groupby('date')['sentiment_score'].mean().reset_index()
    return trend.sort_values('date').to_dict(orient='records')

@app.get("/churn-risk")
def get_churn_risk():
    customers = list(customers_col.find())
    reviews = list(reviews_col.find())
    results = []
    for c in customers:
        c_revs = [r for r in reviews if r.get("customer_id") == c.get("customer_id")]
        c_avg = sum(r.get("sentiment_score", 0) for r in c_revs) / len(c_revs) if c_revs else 0.0
        risk_info = calc_churn_for_db(c, c_avg)
        results.append({
            "customer_id": c.get("customer_id"), "name": c.get("name"), "sentiment_score": round(risk_info["avg_sentiment"], 2),
            "ticket_count": c.get("ticket_count", 0), "inactive_days": c.get("inactive_days", 0),
            "churn_risk_pct": round(risk_info["prob"] * 100, 1), "risk_level": risk_info["level"]
        })
    return results

@app.post("/query-ai")
def query_ai(query: AIQuery):
    customers = list(customers_col.find())
    reviews = list(reviews_col.find())
    avg_sentiment = sum(r.get("sentiment_score", 0) for r in reviews) / len(reviews) if reviews else 0.0
    
    high_risk = []
    for c in customers:
        c_revs = [r for r in reviews if r.get("customer_id") == c.get("customer_id")]
        c_avg = sum(r.get("sentiment_score", 0) for r in c_revs) / len(c_revs) if c_revs else 0.0
        if calc_churn_for_db(c, c_avg)["level"] == "High":
            high_risk.append(c.get("name"))
            
    recent_feedback = " ".join([r.get("text", "") for r in reviews[:5]])
            
    context_prompt = f"""
    You are an advanced CX (Customer Experience) Intelligence AI Copilot.
    DATABASE CONTEXT:
    - Total Customers: {len(customers)}
    - Overall Average Sentiment Score: {round(avg_sentiment, 2)}
    - High Risk Churners: {', '.join(high_risk) if high_risk else 'None'}
    - Recent Feedback snippet: "{recent_feedback}"
    
    USER QUESTION: {query.question}
    """
    try:
        response = gemini_model.generate_content(context_prompt)
        return {"answer": response.text}
    except Exception as e:
        return {"answer": "Error connecting to AI."}

@app.get("/journey/{customer_id}")
def get_journey(customer_id: str):
    journeys = list(journeys_col.find({"customer_id": customer_id}))
    for j in journeys: j["id"] = str(j.pop("_id"))
    return journeys if journeys else [{"date": "2023-01-01", "channel": "system", "sentiment": "Neutral", "resolved": "Y", "note": "Account created"}]

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(status_code=400, detail="Only CSV or JSON files are supported.")
    content = await file.read()
    try:
        if file.filename.endswith('.csv'): df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else: df = pd.read_json(io.StringIO(content.decode('utf-8')))
        stats = {"total_rows": len(df), "columns": list(df.columns)}
        return {"status": "success", "filename": file.filename, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
