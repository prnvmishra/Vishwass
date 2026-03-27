import os
import json
import re
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

# We try to route to OpenRouter natively if the key exists, else OpenAI.
openrouter_key = os.getenv("OPENROUTER_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if openrouter_key:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key,
    )
elif openai_key:
    client = AsyncOpenAI(api_key=openai_key)
else:
    client = AsyncOpenAI(api_key="dummy-key")

import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

def fallback_extract(text: str) -> dict:
    company = ""
    email = ""
    salary = ""
    role = ""
    website = ""
    
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    if email_match:
        email = email_match.group(0)
        
    # STRICT salary extraction: MUST be preceded by contextual words
    salary_match = re.search(r'(?i)(?:salary|stipend|compensation|ctc|remuneration|pay|package)[\s\S]{0,50}?(?:Rs\.?|₹|INR|\$)\s*([\d,\.]+)', text)
    if salary_match:
        salary = salary_match.group(1).replace(",", "").split(".")[0]
    else:
        # Fallback Strict: Rs. followed directly by a number, but ONLY if it's > 5000 and has formatting
        s_match = re.search(r'(?:Rs\.?|₹|INR|\$)\s*([1-9][0-9]{1,2}(?:,[0-9]{3})+|[1-9][0-9]{3,7})', text)
        if s_match:
            salary = s_match.group(1).replace(",", "")
            
    if re.search(r'\b(intern(?:ship)?)\b', text, re.IGNORECASE):
        role = "Intern"
    elif re.search(r'\b(fresher|trainee|junior|sde-1)\b', text, re.IGNORECASE):
        role = "Fresher"
    elif re.search(r'\b(developer|engineer|manager|analyst|designer|writer|consultant|executive)\b', text, re.IGNORECASE):
        role_m = re.search(r'\b([A-Za-z]+\s+(?:developer|engineer|manager|analyst|designer|writer|consultant|executive))\b', text, re.IGNORECASE)
        role = role_m.group(1).title() if role_m else "Professional"
    else:
        role = "Unspecified Position"
        
    # 1. Try strict Regex for definitive Company suffix (Title Cased only)
    company_match = re.search(r'\b((?:[A-Z][a-zA-Z0-9&.\-]*[ \t]+){1,4})(Private Limited|Pvt[\.?][ \t]*Ltd[\.?]|LLC|Inc[\.?]|Corp[\.?]|Technologies|Solutions|Group|Consulting)\b', text, re.IGNORECASE)
    if company_match:
        words = company_match.group(1).strip().split()
        if all(w[0].isupper() for w in words):
            company = company_match.group(0).strip()
            
    if not company:
        # 2. Try offer context regex matching only Capitalized proper nouns on SAME line
        alt_comp = re.search(r'(?:offer from|joining|welcome to|at)[ \t]+([A-Z][a-zA-Z0-9&.\-]+(?:[ \t]+[A-Z][a-zA-Z0-9&.\-]+){0,3})', text)
        if alt_comp and "Intern" not in alt_comp.group(1) and "Role" not in alt_comp.group(1):
            company = alt_comp.group(1).strip()
            
    # 3. If STILL no company, use Spacy BUT filter out common random words
    if not company and nlp:
        # replace newlines to stop spacy from getting confused
        clean_text = text.replace("\n", " ")
        doc = nlp(clean_text)
        orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG" and len(ent.text) > 3]
        for o in orgs:
            if not any(x in o.lower() for x in ["dear", "salary", "ctc", "role", "intern", "fresher", "developer", "engineer", "month", "year"]):
                company = o
                break
                
    if not company:
        # 4. Fallback to extracting whatever is on the very first non-empty line
        lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 3]
        if lines:
            company = lines[0].title()
        else:
            company = "Unknown Entity"
            
    # Final cleanup of company name
    company = company.replace("\n", " ").replace("\r", "").strip()
    if company.endswith("."):
        company = company[:-1]
        
    if not company:
        # 4. Fallback to extracting whatever is on the very first non-empty line
        lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 3]
        if lines:
            company = lines[0].title()
        else:
            company = "Unknown Entity"
            
    # Final cleanup of company name
    company = company.replace("\n", " ").replace("\r", "").strip()
    if company.endswith("."):
        company = company[:-1]
        
    website_match = re.search(r'(www\.[a-zA-Z0-9-]+\.[a-zA-Z]+|https?://[a-zA-Z0-9-]+\.[a-zA-Z]+)', text)
    if website_match:
        website = website_match.group(0)

    scam_phrases = ["registration fee", "urgent hiring", "limited seats", "pay to confirm", "security deposit"]
    suspicious = any(p in text.lower() for p in scam_phrases)

    return {
        "extracted_data": {
            "company_name": company,
            "hr_email": email,
            "salary": salary,
            "role": role,
            "website": website,
            "mca_registration": "Verification Backend Offline (Regex)"
        },
        "explanation": "Extracted securely using Strict NLP Regex and Spacy. OpenAI API key not detected.",
        "suspicious_wording_found": suspicious
    }

async def analyze_offer_with_llm(text: str) -> dict:
    current_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    current_model = "google/gemini-2.5-flash" if os.getenv("OPENROUTER_API_KEY") else "gpt-4o-mini"
    
    if current_key and current_key != "dummy-key":
        prompt = f"""
        You are an expert HR Risk Analyst.
        Extract the following data from the text below and return it as a JSON block precisely according to this structure. Do NOT wrap it in markdown.
        {{
            "extracted_data": {{
                "company_name": "The popular brand or commercial name of the company (e.g., BYJU'S, Amazon). Do NOT include 'Private Limited'.",
                "hr_email": "The literal HR email (if visible).",
                "salary": "The literal salary/stipend amount or compensation string extracted (e.g., 500,000 INR, 25k/month, 3 LPA).",
                "role": "The primary Job Title or Role discussed (e.g., BDA, Business Development Associate, Software Engineer). Even if it is a probationary term converting to this role later, EXTRACT THIS ROLE AS THE TITLE. Keep it under 4 words.",
                "website": "The official website URL of the company.",
                "linkedin_url": "The EXACT official LinkedIn URL for this company (e.g., https://www.linkedin.com/company/byjus) generated from your knowledge. Output 'Unknown' if you are unsure.",
                "mca_registration": "Evaluate if the company is an officially registered MCA Indian Entity. Massive global multinationals (like Amazon, Google) ALWAYS have verified Indian subsidiaries (e.g., Amazon Development Centre India). If they have an Indian corporate footprint, output 'Verified MCA Entity' with their subsidiary name. Otherwise 'Registration Unknown/Suspicious'."
            }},
            "explanation": "Brief reasoning about any suspicious tone, unrealistic guarantees, or lack of professional standard.",
            "suspicious_wording_found": true/false
        }}
        
        Text:
        {text}
        """
        try:
            response = await client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": "You are a cyber-security and HR system that outputs ONLY raw JSON without any markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=800
            )
            raw_content = response.choices[0].message.content
            # Cleanup any potential markdown block wrappers from OpenRouter models
            clean_content = raw_content.replace('```json', '').replace('```', '').strip()
            
            # Additional cleanup for hidden chars
            if clean_content.startswith('{') and clean_content.endswith('}'):
                pass
            else:
                start = clean_content.find('{')
                # The provided edit suggests returning fallback_extract here if not a clean JSON.
                # This changes the original logic of trying to extract a substring.
                return fallback_extract(text)
            
            # The provided edit replaces the direct json.loads(clean_content) with a regex search.
            # This also implies 'content' variable should be used, which is 'clean_content' here.
            json_match = re.search(r'\{.*\}', clean_content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    return fallback_extract(text)
            return fallback_extract(text) # If no JSON found by regex
        except Exception as e:
            print(f"LLM Error/Timeout: {e}")
            return fallback_extract(text)
    else:
        return fallback_extract(text)

async def generate_company_intelligence(company_name: str, wiki_summary: str) -> dict:
    """Uses LLM to extract massive structured details about a company based on its name and wiki context."""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENROUTER_API_KEY and not OPENAI_API_KEY:
        return {
            "size": "Unknown",
            "headquarters": "Unknown",
            "branches": "Unknown",
            "industry": "Unknown",
            "mca_registration": "No API Keys provided for deep AI profiling.",
            "linkedin_url": "Unknown",
            "official_website": "Unknown",
            "summary": wiki_summary or "No API Keys provided for deep AI profiling."
        }

    prompt = f"""
    You are an OSINT Corporate Intelligence AI. Analyze the company '{company_name}'.
    Context from Wikipedia: {wiki_summary}
    
    Return a literal JSON document containing exactly these keys about the organization:
    - size: (e.g., 'Massive (300,000+ employees)', 'Startup')
    - headquarters: (e.g., 'Bangalore, India')
    - branches: (Detailed string summarizing their global/India branch presence)
    - industry: (e.g., 'IT Services & Consulting')
    - mca_registration: (Check if they are registered with the Indian Ministry of Corporate Affairs (MCA). Massive global multinationals (like Amazon, Google) ALWAYS have verified Indian subsidiaries. If you are 100% CERTAIN of their Indian corporate footprint, output 'Verified Ministry of Corporate Affairs (MCA) Entity' and include their Indian subsidiary name. CRITICAL: DO NOT GENERATE OR GUESS A CIN (Corporate Identification Number) UNDER ANY CIRCUMSTANCES. If you are NOT 100% certain, or if they are a foreign company with no legally verified Indian branch (e.g., WPS Office, Kingsoft), you must NOT guess. Output 'No Verified MCA Registration Found - Proceed with Caution'.)
    - linkedin_url: (The EXACT official LinkedIn URL for this company, e.g. https://www.linkedin.com/company/byjus)
    - official_website: (The EXACT official website URL for this company)
    - summary: (A crisp 2-sentence description of what they do)
    
    Only output the JSON object. Do not output anything else.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY or OPENAI_API_KEY}"
    }

    try:
        url = "https://openrouter.ai/api/v1/chat/completions" if OPENROUTER_API_KEY else "https://api.openai.com/v1/chat/completions"
        if OPENROUTER_API_KEY:
            headers["HTTP-Referer"] = "https://vishwas.app"
            headers["X-Title"] = "Vishwas Scanner"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json={
                    "model": "google/gemini-2.5-flash" if OPENROUTER_API_KEY else "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 600,
                    "temperature": 0.0
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
    except Exception as e:
        print(f"Intelligence Profiling Error: {e}")
        pass

    return {
        "size": "Unknown",
        "headquarters": "Unknown",
        "branches": "Unknown",
        "industry": "Unknown",
        "mca_registration": "Verification Backend Offline.",
        "summary": wiki_summary or "Entity intelligence generation failed."
    }
