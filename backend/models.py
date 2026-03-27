from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ExtractedData(BaseModel):
    company_name: Optional[str] = None
    hr_email: Optional[str] = None
    salary: Optional[str] = None
    role: Optional[str] = None
    website: Optional[str] = None
    mca_registration: Optional[str] = None

class VerifiedLinks(BaseModel):
    website: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None

class IPQSFraudIntel(BaseModel):
    fraud_score: int
    is_disposable: bool
    recent_abuse: bool

class LinkedInJobsIntel(BaseModel):
    has_active_listings: bool
    message: str

class AnalyzeResponse(BaseModel):
    score: int
    risk_level: str
    extracted_data: ExtractedData
    reasons: List[str]
    raw_text: Optional[str] = None
    llm_analysis: Optional[str] = None
    verified_links: Optional[VerifiedLinks] = None
    ipqs_intel: Optional[IPQSFraudIntel] = None
    linkedin_jobs: Optional[LinkedInJobsIntel] = None
