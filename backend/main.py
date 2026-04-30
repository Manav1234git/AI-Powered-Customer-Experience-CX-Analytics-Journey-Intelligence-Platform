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
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import google.generativeai as genai
from passlib.context import CryptContext
from jose import JWTError, jwt

import models
from database import engine, get_db, Base

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CX Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH SETUP ---
SECRET_KEY = "super-secret-key-for-pilot-presentation-only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

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
def init_db(db: Session):
    # Check for Admin user
    if not db.query(models.User).filter(models.User.email == "admin@cx.com").first():
        hashed_pwd = get_password_hash("admin123")
        admin_user = models.User(email="admin@cx.com", hashed_password=hashed_pwd, full_name="System Admin")
        db.add(admin_user)
        db.commit()

    # Check for customers
    if db.query(models.Customer).first():
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
    for c in customers_data: db.add(models.Customer(**c))
        
    reviews_data = [
        {"customer_id": "C001", "name": "Alice Smith", "text": "Great service, very happy with the product!", "rating": 5, "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.8},
        {"customer_id": "C002", "name": "Bob Jones", "text": "Terrible experience, the worst support ever.", "rating": 1, "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.9},
        {"customer_id": "C003", "name": "Charlie Brown", "text": "Good value for money.", "rating": 4, "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.5},
        {"customer_id": "C004", "name": "Diana Prince", "text": "It was okay, nothing special.", "rating": 3, "date": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"), "sentiment_label": "Neutral", "sentiment_score": 0.0},
        {"customer_id": "C005", "name": "Evan Wright", "text": "Awful platform, so broken.", "rating": 1, "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"), "sentiment_label": "Negative", "sentiment_score": -0.8},
        {"customer_id": "C006", "name": "Fiona Gallagher", "text": "Excellent tools, amazing team.", "rating": 5, "date": (datetime.now() - timedelta(days=18)).strftime("%Y-%m-%d"), "sentiment_label": "Positive", "sentiment_score": 0.9},
    ]
    for r in reviews_data: db.add(models.Review(**r))
        
    journeys_data = [
        {"customer_id": "C001", "date": "2023-10-01", "channel": "email", "sentiment": "Neutral", "resolved": "Y", "note": ""},
        {"customer_id": "C001", "date": "2023-10-15", "channel": "chat", "sentiment": "Positive", "resolved": "Y", "note": ""},
        {"customer_id": "C002", "date": "2023-09-20", "channel": "phone", "sentiment": "Negative", "resolved": "N", "note": ""},
    ]
    for j in journeys_data: db.add(models.JourneyTouchpoint(**j))
        
    db.commit()

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
        features = pd.DataFrame([{'ticket_count': customer.ticket_count, 'inactive_days': customer.inactive_days, 'avg_sentiment': avg_sentiment}])
        X_scaled = scaler.transform(features)
        prob = churn_model.predict_proba(X_scaled)[0][1]
    else:
        x = 0.3 * customer.ticket_count + 0.4 * (customer.inactive_days / 30) - 0.5 * avg_sentiment
        prob = 1 / (1 + math.exp(-x))
    
    if prob < 0.3: level = "Low"
    elif prob <= 0.6: level = "Medium"
    else: level = "High"
    return {"prob": prob, "level": level, "avg_sentiment": avg_sentiment}

# --- Pydantic Models ---
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
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
    db = next(get_db())
    init_db(db)

# AUTH ENDPOINTS
@app.post("/api/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": new_user.email}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": new_user.email, "name": new_user.full_name}}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": user.email, "name": user.full_name}}

# PROTECTED DEPENDENCY
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/api/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {"email": current_user.email, "name": current_user.full_name}

# DATA ENDPOINTS (Protected theoretically, but left public for demo simplicity or we can protect them)
# For the demo presentation, let's keep the API public so the React app works without huge state changes everywhere,
# but we will add actual authentication flow for the frontend landing page.

@app.post("/submit-review")
def submit_review(review: ReviewInput, db: Session = Depends(get_db)):
    score, label = calculate_sentiment(review.text)
    new_rev = models.Review(
        customer_id=review.customer_id, name=review.name, text=review.text, rating=review.rating,
        date=review.date, sentiment_label=label, sentiment_score=score
    )
    db.add(new_rev)
    cust = db.query(models.Customer).filter(models.Customer.customer_id == review.customer_id).first()
    if not cust:
        cust = models.Customer(customer_id=review.customer_id, name=review.name, ticket_count=0, inactive_days=0)
        db.add(cust)
    db.commit()
    return {"status": "success", "review": new_rev}

@app.get("/reviews")
def get_reviews(db: Session = Depends(get_db)):
    return db.query(models.Review).order_by(models.Review.id.desc()).all()

@app.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    reviews = db.query(models.Review).all()
    total_customers = len(customers)
    avg_sentiment = sum(r.sentiment_score for r in reviews) / len(reviews) if reviews else 0.0
    
    all_churns = []
    for c in customers:
        c_revs = [r for r in reviews if r.customer_id == c.customer_id]
        c_avg = sum(r.sentiment_score for r in c_revs) / len(c_revs) if c_revs else 0.0
        all_churns.append(calc_churn_for_db(c, c_avg)["prob"])
    avg_churn_risk = sum(all_churns) / len(all_churns) if all_churns else 0.0
    
    nps = 0.0
    if reviews:
        promoters = sum(1 for r in reviews if r.rating >= 4)
        detractors = sum(1 for r in reviews if r.rating <= 2)
        nps = ((promoters - detractors) / len(reviews)) * 100

    return {
        "total_customers": total_customers,
        "avg_sentiment": round(avg_sentiment, 2),
        "avg_churn_risk": round(avg_churn_risk * 100, 1),
        "nps_score": round(nps, 1)
    }

@app.get("/sentiment-trend")
def get_sentiment_trend(db: Session = Depends(get_db)):
    reviews = db.query(models.Review).all()
    if not reviews: return []
    df = pd.DataFrame([{ "date": r.date, "sentiment_score": r.sentiment_score } for r in reviews])
    trend = df.groupby('date')['sentiment_score'].mean().reset_index()
    return trend.sort_values('date').to_dict(orient='records')

@app.get("/churn-risk")
def get_churn_risk(db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    reviews = db.query(models.Review).all()
    results = []
    for c in customers:
        c_revs = [r for r in reviews if r.customer_id == c.customer_id]
        c_avg = sum(r.sentiment_score for r in c_revs) / len(c_revs) if c_revs else 0.0
        risk_info = calc_churn_for_db(c, c_avg)
        results.append({
            "customer_id": c.customer_id, "name": c.name, "sentiment_score": round(risk_info["avg_sentiment"], 2),
            "ticket_count": c.ticket_count, "inactive_days": c.inactive_days,
            "churn_risk_pct": round(risk_info["prob"] * 100, 1), "risk_level": risk_info["level"]
        })
    return results

@app.post("/query-ai")
def query_ai(query: AIQuery, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    reviews = db.query(models.Review).all()
    avg_sentiment = sum(r.sentiment_score for r in reviews) / len(reviews) if reviews else 0.0
    
    high_risk = [c.name for c in customers if calc_churn_for_db(c, sum(r.sentiment_score for r in reviews if r.customer_id == c.customer_id) / max(1, len([r for r in reviews if r.customer_id == c.customer_id])))["level"] == "High"]
    recent_feedback = " ".join([r.text for r in reviews[:5]])
            
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
def get_journey(customer_id: str, db: Session = Depends(get_db)):
    journeys = db.query(models.JourneyTouchpoint).filter(models.JourneyTouchpoint.customer_id == customer_id).all()
    return journeys if journeys else [{"date": "2023-01-01", "channel": "system", "sentiment": "Neutral", "resolved": "Y", "note": "Account created"}]
