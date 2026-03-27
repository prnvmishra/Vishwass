from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    score = Column(Integer)
    risk_level = Column(String)
    reasons = Column(JSON)  # Will store list of strings
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ScamReport(Base):
    __tablename__ = "scam_reports"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    description = Column(Text)
    reporter_email = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
