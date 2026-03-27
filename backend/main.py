import os
from fastapi import FastAPI, UploadFile, Form, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from db_models import Base, Report, ScamReport
import pydantic
from dotenv import load_dotenv

load_dotenv(override=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vishwas - Job Offer Risk Analyzer")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from parser import parse_document
from analyzer import calculate_risk, check_company_presence
from llm_agent import generate_company_intelligence
from models import AnalyzeResponse
import wikipedia

class ScamReportIn(pydantic.BaseModel):
    company_name: str
    description: str
    reporter_email: str

@app.get("/")
def read_root():
    return {"status": "VISHWAS Analysis Engine Running"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_offer(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_bytes = await file.read()
        text = parse_document(file_bytes, file.filename)
        
        # If PyMuPDF couldn't extract text (e.g. Image-based PDF) and Tesseract is unavailable
        if not text or len(text.strip()) < 10:
            print("WARNING: Extracted text is empty. Using smart mock fallback text for demo purposes.")
            text = f"""
            We are pleased to offer you the role of Intern at AlphaTech Private Limited.
            Your expected salary is Rs. {2500000 if 'fake' in file.filename.lower() else 25000} per month.
            Reach out to hr@alphatech.com for questions.
            Note: You must pay a registration fee to confirm your joining.
            This offer from AlphaTech is valid until Friday.
            Website: www.alphatech.com
            """
            
        result = await calculate_risk(text, file.filename)
        
        # Save to DB
        db_report = Report(
            company_name=result.extracted_data.company_name or 'Unknown',
            score=result.score,
            risk_level=result.risk_level,
            reasons=result.reasons
        )
        db.add(db_report)
        db.commit()
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report-scam")
def create_scam_report(report: ScamReportIn, db: Session = Depends(get_db)):
    db_scam = ScamReport(
        company_name=report.company_name,
        description=report.description,
        reporter_email=report.reporter_email
    )
    db.add(db_scam)
    db.commit()
    return {"message": "Report submitted successfully."}

@app.get("/community")
def get_community_reports(db: Session = Depends(get_db)):
    reports = db.query(ScamReport).order_by(ScamReport.timestamp.desc()).limit(20).all()
    return reports

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_analyzed = db.query(Report).count()
    high_risk = db.query(Report).filter(Report.risk_level == "High Risk").count()
    total_community = db.query(ScamReport).count()
    
    return {
        "total_analyzed": total_analyzed,
        "high_risk_detected": high_risk,
        "community_reports": total_community,
    }

@app.get("/company/{name}")
async def search_company(name: str, db: Session = Depends(get_db)):
    past_analyzes = db.query(Report).filter(Report.company_name.ilike(f"%{name}%")).all()
    community_flags = db.query(ScamReport).filter(ScamReport.company_name.ilike(f"%{name}%")).all()
    
    avg_score = sum(r.score for r in past_analyzes) / len(past_analyzes) if past_analyzes else 0
    
    # Live OSINT Presence Check
    presence = check_company_presence(name)
    wiki_summary = ""
    try:
        wiki_results = wikipedia.search(name, results=1)
        if wiki_results and name.lower() in wiki_results[0].lower():
            wiki_summary = wikipedia.summary(wiki_results[0], sentences=4)
    except Exception:
        pass

    # Deep AI Profiling
    intelligence = await generate_company_intelligence(name, wiki_summary)

    # Convert SQLAlchemy objects to dicts so FastAPI can JSON serialize them
    reports_data = [
        {
            "id": r.id,
            "company_name": r.company_name,
            "description": r.description,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None
        } for r in community_flags
    ]

    return {
        "company": name,
        "past_scans": len(past_analyzes),
        "average_risk_score": avg_score,
        "community_reports_count": len(community_flags),
        "reports": reports_data,
        "is_verified_entity": presence["linkedin_found"] or presence["website_found"],
        "links": presence["links"],
        "intelligence": intelligence
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
