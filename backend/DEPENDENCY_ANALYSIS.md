# VISHWAS Dependencies Analysis

## Critical Dependencies & Their Functions

### 1. **Document Processing**
```
pymupdf          - PDF text extraction
pdfplumber       - PDF parsing
pytesseract      - OCR (image to text)
opencv-python    - Image preprocessing
```
**Problem**: बिना इनके PDF और image files process नहीं होंगी

### 2. **AI/NLP Processing**
```
spacy            - Advanced NLP, entity extraction
en_core_web_sm   - English language model
openai           - LLM analysis
```
**Problem**: बिना इनके intelligent analysis नहीं होगा

### 3. **External APIs**
```
googlesearch-python   - Company search
duckduckgo-search     - Backup search
wikipedia            - Company info
httpx                - API calls
```
**Problem**: Company verification limited हो जाएगा

## Solutions for Proper Hosting

### Option 1: **Serverless Functions** (Recommended)
Split into multiple functions:
```
1. Document Parser (separate service)
2. AI Analysis (OpenAI API only)
3. Risk Calculator (lightweight)
```

### Option 2: **Microservices Architecture**
```
Frontend → API Gateway → Multiple Services
├── Document Service (heavy)
├── AI Service (medium)  
├── Risk Service (light)
└── Database Service
```

### Option 3: **Hybrid Approach**
```
Local Processing + Cloud APIs
├── Basic parsing locally
├── Heavy processing via APIs
└── AI via OpenAI only
```

## Recommended Architecture for Hosting

### Phase 1: **MVP with APIs**
```python
# Replace heavy dependencies with API calls
- PDF → PDF.co API or Adobe PDF Services
- OCR → Google Vision API or Tesseract Cloud
- NLP → OpenAI GPT-4 only
- Search → Google Search API
```

### Phase 2: **Gradual Migration**
```python
# Keep some processing, move heavy parts
- Light PDF processing locally
- OCR via API
- NLP via OpenAI
- Search via multiple APIs
```

## Cost Analysis

### Current Approach (Full Dependencies)
- Server: $20-50/month (for memory)
- Storage: $10/month
- APIs: $20-100/month
- **Total: $50-160/month**

### API-First Approach  
- Server: $5-10/month (lightweight)
- APIs: $30-80/month
- **Total: $35-90/month**

### Hybrid Approach
- Server: $10-20/month
- APIs: $15-50/month  
- **Total: $25-70/month**

## Implementation Strategy

### Step 1: **API Integration**
```python
# Replace PyMuPDF with PDF.co
def extract_pdf_text(file_bytes):
    import requests
    response = requests.post(
        'https://api.pdf.co/v1/pdf/convert/to/text',
        files={'file': file_bytes},
        headers={'x-api-key': PDF_CO_API_KEY}
    )
    return response.json()['body']

# Replace Tesseract with Vision API
def extract_image_text(image_bytes):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    # ... API call
```

### Step 2: **Smart Caching**
```python
# Cache results to reduce API calls
import redis
cache = redis.Redis()

def analyze_company_cached(company_name):
    cached = cache.get(f"company:{company_name}")
    if cached:
        return json.loads(cached)
    
    result = analyze_company_api(company_name)
    cache.setex(f"company:{company_name}", 86400, json.dumps(result))
    return result
```

### Step 3: **Fallback System**
```python
def smart_extract_text(file_bytes, filename):
    try:
        # Try API first
        return extract_via_api(file_bytes)
    except:
        try:
            # Fallback to local if available
            return extract_local(file_bytes)
        except:
            # Final fallback
            return "Unable to extract text"
```

## Recommended Final Architecture

```
Frontend (Vercel)
    ↓
API Gateway (Cloudflare Workers)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│  Document API   │   Analysis API  │  Search API     │
│  (PDF.co)       │   (OpenAI)      │  (Google)       │
│  $10/month      │   $20/month     │  $5/month       │
└─────────────────┴─────────────────┴─────────────────┘
    ↓
Database (Supabase Free)
```

This approach:
✅ Reduces server costs
✅ Scales automatically  
✅ More reliable
✅ Easier to maintain
✅ Better performance
