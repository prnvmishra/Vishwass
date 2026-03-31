import os
import json
import asyncio
import io
import re
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Document Processing
import fitz  # PyMuPDF
import PyPDF2

# AI & APIs
import httpx
import openai
import spacy
from google.cloud import vision

# Web Search & APIs
import googlesearch
from duckduckgo_search import DDGS
import wikipedia

# Email & Job Verification APIs
async def check_email_ipqs_render(email: str) -> dict:
    """IPQS email validation for Render"""
    try:
        ipqs_key = os.getenv("IPQS_API_KEY")
        if not ipqs_key:
            return {"valid": False, "reason": "IPQS API key not configured"}
            
        url = f"https://www.ipqualityscore.com/api/json/email/{ipqs_key}/{email}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return response.json()
    except Exception as e:
        print(f"IPQS Error: {e}")
        return {"valid": False, "reason": "IPQS service unavailable"}

async def check_linkedin_jobs_render(company_name: str, role: str) -> dict:
    """LinkedIn jobs verification for Render"""
    try:
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if not rapidapi_key:
            return {"has_jobs": False, "reason": "RapidAPI key not configured"}
            
        url = "https://jsearch.p.rapidapi.com/search"
        querystring = {
            "query": f"{role} at {company_name}", 
            "page": "1", 
            "num_pages": "1"
        }
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=querystring)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("data", [])
                return {"has_jobs": len(jobs) > 0, "count": len(jobs)}
    except Exception as e:
        print(f"JSearch API Error: {e}")
    return {"has_jobs": False, "reason": "Job search service unavailable"}

app = FastAPI(title="VISHWAS - Render Free Tier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Warning: spaCy model not loaded")

# Initialize Google Vision (if credentials available)
vision_client = None
try:
    vision_client = vision.ImageAnnotatorClient()
except:
    print("Google Vision not configured - using fallback")

# Lightweight document parser
def parse_document_render(file_bytes: bytes, filename: str) -> str:
    """Document processing optimized for Render free tier"""
    
    if filename.lower().endswith('.txt'):
        return file_bytes.decode('utf-8', errors='ignore')
    
    elif filename.lower().endswith('.pdf'):
        extracted_text = ""
        
        # Method 1: PyMuPDF with enhanced extraction
        try:
            pdf_stream = io.BytesIO(file_bytes)
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            
            for page_num, page in enumerate(doc):
                # Extract text with multiple methods
                page_text = page.get_text()
                extracted_text += page_text
                
                # Try different text extraction options
                if len(page_text.strip()) < 50:
                    # Try with different extraction flags
                    page_text = page.get_text(textflags=fitz.TEXTFLAGS_TEXT)
                    extracted_text += page_text
                    
                    if len(page_text.strip()) < 50:
                        # Try with words extraction
                        words = page.get_text("words")
                        if words:
                            word_text = " ".join([w[4] for w in words])
                            extracted_text += word_text
                
                # Extract images and perform OCR if needed
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # Check if not CMYK
                            img_data = pix.tobytes("png")
                            
                            # Use Google Vision for OCR on image
                            if vision_client:
                                try:
                                    from google.cloud.vision import types
                                    image = types.Image(content=img_data)
                                    response = vision_client.text_detection(image=image)
                                    texts = response.text_annotations
                                    if texts:
                                        extracted_text += "\n" + texts[0].description
                                except Exception as e:
                                    print(f"Google Vision OCR error: {e}")
                            else:
                                # Fallback: Try to extract basic text from image using OCR library if available
                                try:
                                    import pytesseract
                                    import PIL.Image
                                    import io
                                    img_pil = PIL.Image.open(io.BytesIO(img_data))
                                    ocr_text = pytesseract.image_to_string(img_pil)
                                    if ocr_text.strip():
                                        extracted_text += "\n" + ocr_text.strip()
                                except ImportError:
                                    print("Tesseract not available for OCR fallback")
                                except Exception as e:
                                    print(f"Tesseract OCR error: {e}")
                        
                        pix = None  # Free memory
                    except Exception as e:
                        print(f"Image extraction error: {e}")
            
            if len(extracted_text.strip()) > 50:
                return extracted_text
        except Exception as e:
            print(f"PyMuPDF error: {e}")
        
        # Method 2: PyPDF2 (fallback)
        try:
            pdf_stream = io.BytesIO(file_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
            if len(extracted_text.strip()) > 50:
                return extracted_text
        except Exception as e:
            print(f"PyPDF2 error: {e}")
        
        # Method 3: Try to extract any readable text from PDF metadata
        try:
            import pdfplumber
            pdf_stream = io.BytesIO(file_bytes)
            with pdfplumber.open(pdf_stream) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        extracted_text += page.extract_text() + "\n"
                if len(extracted_text.strip()) > 50:
                    return extracted_text
        except ImportError:
            print("pdfplumber not available")
        except Exception as e:
            print(f"pdfplumber error: {e}")
        
        return f"Unable to extract text from PDF: {filename}"
    
    elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
        # Google Vision API for OCR
        if vision_client:
            try:
                from google.cloud.vision import types
                image = types.Image(content=file_bytes)
                response = vision_client.text_detection(image=image)
                texts = response.text_annotations
                if texts:
                    return texts[0].description
            except Exception as e:
                print(f"Google Vision error: {e}")
        
        return f"Unable to extract text from image: {filename}"
    
    else:
        try:
            if isinstance(file_bytes, bytes):
                decoded_text = file_bytes.decode('utf-8', errors='ignore')
                if len(decoded_text.strip()) > 50:
                    return decoded_text
        except:
            pass
        return f"Unsupported file type: {filename}"

# Analysis with AI
async def analyze_document_render(text: str, filename: str) -> dict:
    """Analysis optimized for Render free tier"""
    
    # Initialize all variables at the start
    company_name = "Unknown"
    role = "Unknown" 
    salary = ""
    website = ""
    email = ""
    
    # Enhanced regex patterns for extraction
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    all_emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    
    # Prioritize HR-specific emails
    email = ""
    if all_emails:
        # Look for HR-specific emails first
        hr_keywords = ['hr', 'human', 'resource', 'recruit', 'career', 'talent', 'hiring']
        for found_email in all_emails:
            email_prefix = found_email.split('@')[0].lower()
            if any(keyword in email_prefix for keyword in hr_keywords):
                email = found_email
                break
        
        # If no HR email found, use the first email
        if not email:
            email = all_emails[0]
    
    # Multiple salary patterns
    salary_patterns = [
        r'(?:Rs\.?|₹|INR)\s*([\d,\.]+)\s*(?:per\s*month|monthly|annually|per\s*year|yearly)?',
        r'\$?\s*([\d,\.]+)\s*(?:per\s*month|monthly|annually|per\s*year|yearly|USD|per\s*annum)',
        r'salary[:\s]*([\d,\.]+)',
        r'compensation[:\s]*([\d,\.]+)'
    ]
    salary = ""
    for pattern in salary_patterns:
        salary_match = re.search(pattern, text, re.IGNORECASE)
        if salary_match:
            salary = salary_match.group(1)
            break
    
    # Enhanced website extraction
    website_patterns = [
        r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'website[:\s]*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'official\s+site[:\s]*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    ]
    website = ""
    for pattern in website_patterns:
        website_match = re.search(pattern, text, re.IGNORECASE)
        if website_match:
            website = website_match.group(0) if pattern.startswith(('www', 'http')) else website_match.group(1)
            if not website.startswith(('http', 'www')):
                website = 'www.' + website
            break
    
    # Enhanced company name extraction
    company_patterns = [
        r'([A-Z][a-zA-Z\s&]+(?:Private\s+Limited|Ltd\.?|LLC|Inc\.?|Corp\.?|Corporation))',
        r'([A-Z][a-zA-Z\s&]+(?:Technologies|Solutions|Systems|Services|Global))',
        r'company[:\s]*([A-Z][a-zA-Z\s&]+)',
        r'offer.*?from\s+([A-Z][a-zA-Z\s&]+)',
        r'hiring.*?at\s+([A-Z][a-zA-Z\s&]+)'
    ]
    
    for pattern in company_patterns:
        company_match = re.search(pattern, text, re.IGNORECASE)
        if company_match:
            company_name = company_match.group(1).strip()
            break
    
    # Fallback to NLP if regex fails
    if company_name == "Unknown":
        try:
            doc = nlp(text)
            organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            if organizations:
                company_name = organizations[0]
        except Exception as e:
            print(f"NLP error: {e}")
    
    # Enhanced role extraction
    role_patterns = [
        r'(?:role|position)\s+(?:of|as)\s+([A-Za-z\s]+)',
        r'hiring\s+(?:for|a)\s+([A-Za-z\s]+)',
        r'(?:we are|looking for)\s+(?:a\s+)?([A-Za-z\s]+)',
        r'position[:\s]*([A-Za-z\s]+)',
        r'job[:\s]*([A-Za-z\s]+)'
    ]
    
    for pattern in role_patterns:
        role_match = re.search(pattern, text, re.IGNORECASE)
        if role_match:
            role = role_match.group(1).strip()
            # Clean up role name
            role = re.sub(r'\b(at|in|for|of|with)\b.*$', '', role, flags=re.IGNORECASE).strip()
            if len(role) > 3:  # Ensure meaningful role name
                break
    
    # OpenRouter AI Analysis
    ai_analysis = "AI analysis unavailable"
    risk_score = 0
    
    try:
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        print(f"OpenRouter key found: {bool(openrouter_key)}")
        print(f"Text length: {len(text.strip())}")
        
        if openrouter_key and len(text.strip()) > 20:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://vishwass.onrender.com",
                        "X-Title": "VISHWAS Job Analyzer"
                    },
                    json={
                        "model": "openai/gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "user", 
                                "content": f"Analyze this job offer for legitimacy and extract key details:\n\n{text[:1500]}\n\nReturn JSON with: risk_score (0-100), company_name, role, salary, is_legitimate, concerns"
                            }
                        ]
                    }
                )
                
                print(f"OpenRouter response status: {response.status_code}")
                
                if response.status_code == 200:
                    ai_result = response.json()
                    ai_analysis = ai_result["choices"][0]["message"]["content"]
                    print(f"AI Analysis: {ai_analysis}")
                    
                    # Parse AI response
                    try:
                        import json
                        ai_data = json.loads(ai_analysis)
                        risk_score = ai_data.get("risk_score", 0)
                        if ai_data.get("company_name"):
                            company_name = ai_data["company_name"]
                        if ai_data.get("role"):
                            role = ai_data["role"]
                        if ai_data.get("salary"):
                            salary = ai_data["salary"]
                    except:
                        pass
                else:
                    print(f"OpenRouter error: {response.text}")
    except Exception as e:
        print(f"AI analysis error: {e}")
        ai_analysis = f"AI analysis failed: {str(e)}"
    
    # Email validation with IPQS
    ipqs_intel = None
    if email:
        ipqs_intel = await check_email_ipqs_render(email)
    
    # Job verification with RapidAPI
    linkedin_jobs = None
    if company_name != "Unknown" and role != "Unknown":
        linkedin_jobs = await check_linkedin_jobs_render(company_name, role)
    
    # Basic risk scoring
    if risk_score == 0:
        scam_phrases = ["registration fee", "urgent hiring", "limited seats", "pay to confirm"]
        if any(phrase in text.lower() for phrase in scam_phrases):
            risk_score += 40
        if "@gmail.com" in email or "@yahoo.com" in email:
            risk_score += 20
        if ipqs_intel and not ipqs_intel.get("valid", True):
            risk_score += 30
        if linkedin_jobs and not linkedin_jobs.get("has_jobs", False):
            risk_score += 20
    
    risk_level = "Low Risk" if risk_score < 40 else "Medium Risk" if risk_score < 70 else "High Risk"
    
    return {
        "score": risk_score,
        "risk_level": risk_level,
        "extracted_data": {
            "company_name": company_name,
            "hr_email": email,
            "salary": salary,
            "role": role,
            "website": website
        },
        "reasons": ["Render optimized analysis with Google Vision"],
        "raw_text": text[:300] + "..." if len(text) > 300 else text,
        "llm_analysis": ai_analysis,
        "verified_links": {},
        "ipqs_intel": ipqs_intel,
        "linkedin_jobs": linkedin_jobs
    }

# Simple cache for company intelligence
company_cache = {}

# Company intelligence (optimized for speed)
async def get_company_intelligence_render(name: str) -> dict:
    """Fast company analysis optimized for Render"""
    
    # Check cache first
    if name in company_cache:
        return company_cache[name]
    
    intelligence = {
        "size": "Unknown",
        "headquarters": "Unknown",
        "branches": "Unknown", 
        "industry": "Unknown",
        "mca_registration": "Not verified",
        "linkedin_url": "Unknown",
        "official_website": "Unknown",
        "summary": "No information available"
    }
    
    # Fast Wikipedia search (timeout 3 seconds)
    try:
        import asyncio
        wiki_results = await asyncio.wait_for(
            asyncio.to_thread(wikipedia.search, name, results=1),
            timeout=3.0
        )
        if wiki_results:
            summary = await asyncio.wait_for(
                asyncio.to_thread(wikipedia.summary, wiki_results[0], sentences=2),
                timeout=3.0
            )
            intelligence["summary"] = summary
    except asyncio.TimeoutError:
        print("Wikipedia search timed out")
    except Exception as e:
        print(f"Wikipedia error: {e}")
    
    # Fast web search with timeout (only if no Wikipedia result)
    if intelligence["summary"] == "No information available":
        try:
            search_results = await asyncio.wait_for(
                asyncio.to_thread(googlesearch.search, f"{name} company official website", num_results=1),
                timeout=5.0
            )
            if search_results:
                intelligence["official_website"] = search_results[0]
        except asyncio.TimeoutError:
            print("Google search timed out")
        except Exception as e:
            print(f"Google search error: {e}")
    
    # Cache the result
    company_cache[name] = intelligence
    
    return intelligence

@app.get("/debug")
def debug_endpoint():
    return {
        "status": "Debug endpoint working",
        "vision_client": "Available" if vision_client else "Not available",
        "spacy_model": "Loaded" if 'nlp' in globals() else "Not loaded",
        "env_vars": {
            "OPENROUTER_API_KEY": "Set" if os.getenv("OPENROUTER_API_KEY") else "Not set",
            "IPQS_API_KEY": "Set" if os.getenv("IPQS_API_KEY") else "Not set",
            "RAPIDAPI_KEY": "Set" if os.getenv("RAPIDAPI_KEY") else "Not set"
        }
    }

@app.get("/")
def read_root():
    return {"status": "VISHWAS Render Free Tier Engine Running", "features": ["PDF", "Google Vision OCR", "AI", "NLP", "Web Search"]}

@app.post("/analyze")
async def analyze_offer(file: UploadFile = File(...), firebase_uid: Optional[str] = Form(None)):
    try:
        file_bytes = await file.read()
        text = parse_document_render(file_bytes, file.filename)
        
        if not text or len(text.strip()) < 10:
            text = f"Unable to extract meaningful text from {file.filename}"
        
        result = await analyze_document_render(text, file.filename)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company/{name}")
async def search_company(name: str):
    try:
        intelligence = await get_company_intelligence_render(name)
        
        return {
            "company": name,
            "is_verified_entity": bool(intelligence["official_website"] != "Unknown"),
            "links": {"website": intelligence["official_website"]},
            "intelligence": intelligence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
