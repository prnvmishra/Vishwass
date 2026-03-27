import json
import re
import wikipedia
import httpx
from googlesearch import search
from duckduckgo_search import DDGS
from models import AnalyzeResponse, ExtractedData, VerifiedLinks, IPQSFraudIntel, LinkedInJobsIntel
from llm_agent import analyze_offer_with_llm

async def check_email_ipqs(email: str) -> dict:
    url = f"https://www.ipqualityscore.com/api/json/email/MZjjhI7Wm6I0XyBaX6ejxK9WPRO0EyDo/{email}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return response.json()
    except Exception as e:
        print("IPQS Error:", e)
        return {}

async def check_linkedin_jobs(company_name: str, role: str) -> dict:
    if not company_name or not role: return {}
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {
        "query": f"{role} at {company_name}", 
        "page": "1", 
        "num_pages": "1"
    }
    headers = {
        "x-rapidapi-key": "13f39ed9f4mshf830cc58d889b6ap142c2djsnd0e9c6f8a7ec",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=querystring)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("data", [])
                return {"has_jobs": len(jobs) > 0, "count": len(jobs)}
    except Exception as e:
        print("JSearch API Error:", e)
    return {}

def check_company_presence(company_name: str) -> dict:
    presence = {"website_found": False, "linkedin_found": False, "links": {}}
    if not company_name or len(company_name) < 3 or company_name.lower() in ["unknown", "unknown entity", "could not", "intern", "fresher"]:
        return presence
        
    # 1. Wikipedia strict check for massive companies
    try:
        wiki_results = wikipedia.search(company_name, results=1)
        if wiki_results:
            first_word = company_name.lower().split()[0]
            is_match = (first_word in wiki_results[0].lower() or wiki_results[0].lower() in company_name.lower())
            
            # If the title doesn't neatly match, check the summary text. (e.g. 'Byjus' vs 'Think and Learn Private Limited')
            if not is_match:
                try:
                    summary = wikipedia.summary(wiki_results[0], sentences=2).lower()
                    if first_word in summary:
                        is_match = True
                except:
                    pass
                    
            if is_match:
                presence["website_found"] = True
                presence["linkedin_found"] = True
                page = wikipedia.page(wiki_results[0], auto_suggest=False)
                presence["links"]["website"] = page.url
    except Exception as e:
        print(f"Wiki lookup skipped: {e}")
        
    # 2. Advanced Google Search mapping literal URLs (add instagram search)
    try:
        for url in search(f"{company_name} official website linkedin instagram", num_results=6):
            url_lower = url.lower()
            if "linkedin.com/company" in url_lower and not presence["links"].get("linkedin"):
                presence["linkedin_found"] = True
                presence["links"]["linkedin"] = url
            elif "instagram.com" in url_lower and not presence["links"].get("instagram"):
                presence["links"]["instagram"] = url
            elif company_name.lower()[:4].replace(" ", "") in url_lower and "linkedin" not in url_lower and "instagram" not in url_lower and not presence["links"].get("website"):
                presence["website_found"] = True
                presence["links"]["website"] = url
    except Exception as e:
        print(f"Google Search Error: {e}")
        
    # 3. DuckDuckGo as backup
    if not presence["links"].get("linkedin") or not presence["links"].get("website"):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{company_name} official website linkedin", max_results=5))
                for res in results:
                    url = res.get("href", "").lower()
                    if "linkedin.com/company" in url and not presence["links"].get("linkedin"):
                        presence["linkedin_found"] = True
                        presence["links"]["linkedin"] = res.get("href")
                    elif company_name.lower()[:4].replace(" ", "") in url and "linkedin" not in url and not presence["links"].get("website"):
                        presence["website_found"] = True
                        presence["links"]["website"] = res.get("href")
        except Exception as e:
            pass
            
    # 4. Fallback synthesis mechanism (extracting the first word 'Infosys' from 'Infosys Limited' for the clean URL)
    if presence["linkedin_found"] and not presence["links"].get("linkedin"):
        first_word = company_name.lower().split()[0]
        clean_name = first_word.replace(".", "").replace(",", "").replace("'", "").replace("’", "")
        presence["links"]["linkedin"] = f"https://www.linkedin.com/company/{clean_name}"
        
    return presence

async def calculate_risk(text: str, filename: str) -> AnalyzeResponse:
    # 1. Use LLM or Regex fallback to extract data
    llm_result = await analyze_offer_with_llm(text)
    extracted_dict = llm_result.get("extracted_data", {})
    explanation = llm_result.get("explanation", "")
    
    company = extracted_dict.get("company_name", "") or ""
    email = extracted_dict.get("hr_email", "") or ""
    salary = extracted_dict.get("salary", "") or ""
    website = extracted_dict.get("website", "") or ""
    role = extracted_dict.get("role", "") or ""
    
    data = ExtractedData(
        company_name=company,
        hr_email=email,
        salary=salary,
        role=role,
        website=website
    )
    
    score = 0
    reasons = []
    
    # A. Email Intelligence
    public_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    email_domain = email.split("@")[-1].lower() if "@" in email else ""
    if email_domain in public_domains:
        score += 30
        reasons.append(f"Email uses public domain ({email_domain})")
        
    # NEW: Complete Live IPQS Cyber Scan
    ipqs_intel_model = None
    if email:
        ipqs_data = await check_email_ipqs(email)
        if ipqs_data.get("success"):
            f_score = ipqs_data.get("fraud_score", 0)
            disp = ipqs_data.get("disposable", False)
            abuse = ipqs_data.get("recent_abuse", False)
            
            ipqs_intel_model = IPQSFraudIntel(fraud_score=f_score, is_disposable=disp, recent_abuse=abuse)
            
            if f_score > 70:
                score += 40
                reasons.append(f"CRITICAL CYBER THREAT: IPQS flagged email as Malicious (Fraud Score: {f_score}/100)")
            elif disp:
                score += 30
                reasons.append("Email relies on a temporary disposable address provider.")
            elif abuse:
                score += 30
                reasons.append("Email domain has a history of recent cyber abuse or spam operations.")
        
    # B & C. Domain Consistency & Real Company Presence via Web Search
    presence = check_company_presence(company)
    
    # Overwrite brittle synthesis with LLM intelligence if available
    llm_linkedin = extracted_dict.get("linkedin_url", "")
    if llm_linkedin and "linkedin.com/" in llm_linkedin.lower():
        presence["links"]["linkedin"] = llm_linkedin
        presence["linkedin_found"] = True
        
    llm_web = extracted_dict.get("official_website", "")
    if llm_web and "http" in llm_web.lower():
        presence["links"]["website"] = llm_web
        presence["website_found"] = True

    has_web = presence["website_found"] or bool(website)
    has_li = presence["linkedin_found"]
    
    if company and company.lower() not in ["unknown", "unknown entity", "could not"]:
        if not has_web and not has_li:
            score += 25
            reasons.append(f"No verifiable company online presence (LinkedIn/Web) found for '{company}'")
        elif not has_li:
            score += 15
            reasons.append(f"No official LinkedIn company page found for '{company}'")
    else:
        score += 25
        reasons.append("No readable company name found to verify")
        
    # Domain matching
    if website:
        # crude domain extraction
        website_domain = website.lower().replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0]
        if email_domain and website_domain and email_domain != website_domain and email_domain not in public_domains:
            score += 20
            reasons.append(f"Email domain ({email_domain}) does not match website domain ({website_domain})")
            
    # D. Salary Sanity Check
    # Predefined JSON limits
    expected_salary = {
        "Intern": [10000, 30000],
        "Fresher": [300000, 1000000]
    }
    
    try:
        # extract integer
        sal_numbers = re.findall(r'\d+', salary.replace(",", ""))
        if sal_numbers:
            sal_val = int(sal_numbers[0])
            role_key = None
            if re.search(r'\bintern(ship)?\b', role + " " + text, re.IGNORECASE):
                role_key = "Intern"
            elif re.search(r'\bfresher\b', role + " " + text, re.IGNORECASE):
                role_key = "Fresher"
                
            if role_key:
                min_sal, max_sal = expected_salary[role_key]
                if sal_val < min_sal or sal_val > max_sal:
                    score += 15
                    reasons.append(f"Salary anomaly: {sal_val} is unrealistic for {role_key}")
            else:
                # General check if over 50 lakhs
                if sal_val > 5000000:
                    score += 15
                    reasons.append("Salary exceeds expected range")
    except:
        pass
        
    # E. Scam Language Detection
    scam_phrases = ["registration fee", "urgent hiring", "limited seats", "pay to confirm job"]
    text_lower = text.lower()
    found_scams = [p for p in scam_phrases if p in text_lower]
    if found_scams:
        # The prompt says: Scam language → +10
        score += 10
        reasons.append(f"Suspicious language detected: {', '.join(found_scams)}")
        
    if llm_result.get("suspicious_wording_found") and not found_scams:
        score += 10
        reasons.append("AI detected unprofessional or suspicious wording.")
        
    # F. LinkedIn Active Jobs Check (RapidAPI)
    linkedin_jobs_model = None
    if company and role and len(company) > 2 and company.lower() not in ["unknown", "unknown entity"]:
        job_data = await check_linkedin_jobs(company, role)
        if "has_jobs" in job_data:
            if not job_data["has_jobs"]:
                score += 15
                msg = f"No active LinkedIn job listings found matching '{role}' at '{company}'."
                reasons.append(msg)
                linkedin_jobs_model = LinkedInJobsIntel(has_active_listings=False, message=msg)
            else:
                msg = f"Verified: Found {job_data['count']} active job listings for this company!"
                linkedin_jobs_model = LinkedInJobsIntel(has_active_listings=True, message=msg)
        
    # F. Risk Scoring System conversion
    score = min(score, 100)
    
    if score < 40:
        level = "Low Risk"
    elif score < 70:
        level = "Medium Risk"
    else:
        level = "High Risk"
        
    if not reasons:
        reasons.append("No significant risk signals detected.")
        if explanation and explanation != "No OpenAI API key provided. Falling back to local Regex analysis for data extraction.":
            reasons.append(f"AI Notes: {explanation}")
            
    return AnalyzeResponse(
        score=score,
        risk_level=level,
        extracted_data=data,
        reasons=reasons,
        raw_text=text[:500] + ("..." if len(text) > 500 else ""),
        llm_analysis=explanation,
        verified_links=VerifiedLinks(**presence.get("links", {})),
        ipqs_intel=ipqs_intel_model,
        linkedin_jobs=linkedin_jobs_model
    )
