from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    name = Column(String)
    ticket_count = Column(Integer, default=0)
    inactive_days = Column(Integer, default=0)

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    name = Column(String)
    text = Column(String)
    rating = Column(Integer)
    date = Column(String)
    sentiment_label = Column(String)
    sentiment_score = Column(Float)

class JourneyTouchpoint(Base):
    __tablename__ = "journey_touchpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    date = Column(String)
    channel = Column(String)
    sentiment = Column(String)
    resolved = Column(String)
    note = Column(String, nullable=True)
