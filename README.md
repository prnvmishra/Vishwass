# VISHWAS — AI-Powered Job Offer Risk Analyzer

Vishwas is a production-ready hackathon project designed to analyze job offer letters (PDFs and images) to detect employment scams, verify entity consistency, and perform sanity checks on salaries using a combination of heuristics and an AI (OpenAI GPT) agent.

## 🧱 Folder Structure

```
Vishwas/
├── backend/                # FastAPI Python Backend
│   ├── .env                # (Create this for OPENAI_API_KEY)
│   ├── main.py             # FastAPI entry point & routes
│   ├── analyzer.py         # Multi-signal Risk Analysis Engine
│   ├── parser.py           # PyMuPDF and Tesseract extraction
│   ├── llm_agent.py        # GPT prompt and API integration
│   ├── models.py           # Pydantic schemas
│   └── requirements.txt    # Python deps
└── frontend/               # Next.js 15 Frontend
    ├── app/
    │   ├── layout.tsx      # Root layout
    │   ├── page.tsx        # Main UI, Upload, & Dashboard Result
    │   └── globals.css     # Glassmorphism & Theme Tailwind setup
    ├── components/
    │   ├── UploadArea.tsx  # React dropzone component
    │   ├── RiskGauge.tsx   # SVG animated score gauge
    │   └── TrustGraph.tsx  # Visual entity mapping
    ├── package.json        
    └── tailwind.config.ts  
```

## 🚀 Setup Instructions

### 1. Backend Setup

1. Open a terminal and navigate to the backend folder:
   ```bash
   cd Vishwas/backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up OpenAI API Key (optional but recommended for full AI reasoning):
   Create a `.env` file in the `backend` folder:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
5. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *The backend will be available at `http://localhost:8000`*

*(Note: Tesseract OCR is required for image parsing. If you don't have it installed on your system, PDF parsing will still work via PyMuPDF)*

### 2. Frontend Setup

1. Open a new terminal and navigate to the frontend folder:
   ```bash
   cd Vishwas/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   *The frontend will be available at `http://localhost:3000`*

## 🧠 GPT Prompts Used

The core intelligence of the application relies on the following OpenAI prompt located in `backend/llm_agent.py`:

```text
Analyze the following job offer letter for potential risks and scams.
Focus on:
- Grammar and tone professionalism
- Structure completeness
- Suspicious wording (e.g., "pay to confirm", "urgent hiring")

Extract these fields if present: company_name, hr_email, salary, role, website.
Provide a short explanation of your findings.

OUTPUT FORMAT (JSON ONLY):
{
    "extracted_data": {
        "company_name": "...",
        "hr_email": "...",
        "salary": "...",
        "role": "...",
        "website": "..."
    },
    "explanation": "...",
    "suspicious_wording_found": true
}

OFFER TEXT:
{text}
```

## 🎯 Demo Mode
The UI includes "Try Real Offer" and "Try Fake Offer" buttons for quick hackathon demonstrations without needing actual files or API keys.
