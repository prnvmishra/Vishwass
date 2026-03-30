import os
import json
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(title="Vishwas - Hosting Optimized API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lightweight fallback parser for hosting
def parse_document_lightweight(text: str, filename: str) -> str:
    """Simple text extraction for hosting without heavy dependencies"""
    if filename.lower().endswith('.txt'):
        return text.decode('utf-8', errors='ignore') if isinstance(text, bytes) else text
    else:
        # For other files, return sample text for demo
        return f"Sample offer letter content from {filename}"

# Lightweight analysis without heavy ML models
async def analyze_offer_lightweight(text: str, filename: str) -> dict:
    """Simplified analysis for hosting"""
    
    # Basic regex extraction
    import re
    
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0) if email_match else ""
    
    salary_match = re.search(r'(?:Rs\.?|₹|INR|\$)\s*([\d,\.]+)', text)
    salary = salary_match.group(1) if salary_match else ""
    
    # Basic scam detection
    scam_phrases = ["registration fee", "urgent hiring", "limited seats", "pay to confirm"]
    suspicious = any(phrase in text.lower() for phrase in scam_phrases)
    
    # Simple risk calculation
    risk_score = 0
    reasons = []
    
    if "@gmail.com" in email or "@yahoo.com" in email:
        risk_score += 20
        reasons.append("Using public email domain")
    
    if suspicious:
        risk_score += 40
        reasons.append("Suspicious phrases detected")
    
    if risk_score < 40:
        risk_level = "Low Risk"
    elif risk_score < 70:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"
    
    return {
        "score": risk_score,
        "risk_level": risk_level,
        "extracted_data": {
            "company_name": "Sample Company",
            "hr_email": email,
            "salary": salary,
            "role": "Sample Role",
            "website": ""
        },
        "reasons": reasons,
        "raw_text": text[:200] + "..." if len(text) > 200 else text,
        "llm_analysis": "Hosting optimized analysis - Limited functionality",
        "verified_links": {},
        "ipqs_intel": None,
        "linkedin_jobs": None
    }

@app.get("/")
def read_root():
    return {"status": "VISHWAS Hosting Optimized Engine Running"}

@app.post("/analyze")
async def analyze_offer(file: UploadFile = File(...), firebase_uid: Optional[str] = Form(None)):
    try:
        file_bytes = await file.read()
        text = parse_document_lightweight(file_bytes, file.filename)
        
        if not text or len(text.strip()) < 10:
            text = f"""
            We are pleased to offer you the role of Intern at AlphaTech Private Limited.
            Your expected salary is Rs. 25000 per month.
            Reach out to hr@alphatech.com for questions.
            Note: You must pay a registration fee to confirm your joining.
            Website: www.alphatech.com
            """
            
        result = await analyze_offer_lightweight(text, file.filename)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company/{name}")
async def search_company(name: str):
    return {
        "company": name,
        "is_verified_entity": False,
        "links": {},
        "intelligence": {
            "size": "Unknown",
            "headquarters": "Unknown", 
            "branches": "Unknown",
            "industry": "Unknown",
            "mca_registration": "Hosting mode - Verification offline",
            "linkedin_url": "Unknown",
            "official_website": "Unknown",
            "summary": "Company intelligence unavailable in hosting mode"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
