# VISHWAS Hosting Guide

## Problem Analysis
Your project has heavy dependencies that won't work on free hosting:
- OpenCV (100MB+)
- spaCy NLP models (50MB+) 
- Tesseract OCR (system binaries)
- Multiple external API keys required

## Solutions

### Option 1: Free Hosting (Recommended)
**Frontend**: Vercel (Free)
**Backend**: Render (Free) - with optimized version

#### Steps:
1. **Backend Setup for Render**
```bash
# Use optimized files
cd backend
cp main-hosting.py main.py
cp requirements-hosting.txt requirements.txt
```

2. **Deploy to Render**
- Create new Web Service on Render
- Connect your GitHub repo
- Use build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Frontend Setup for Vercel**
```bash
cd frontend
cp next.config.hosting.js next.config.js
```

4. **Deploy to Vercel**
- Connect your GitHub repo to Vercel
- Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`

### Option 2: Full Features (Paid)
**Railway** or **AWS** - supports heavy dependencies and larger memory

#### Requirements:
- Railway Pro plan ($20/month)
- Or AWS EC2 (t3.medium - $30/month)

## Environment Variables Needed

### Backend (.env)
```
OPENAI_API_KEY=your_openai_key
OPENROUTER_API_KEY=your_openrouter_key
IPQS_API_KEY=your_ipqs_key
RAPIDAPI_KEY=your_rapidapi_key
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_key
```

## Limitations in Free Mode

### What Works:
- Basic document upload
- Simple regex analysis
- Basic risk scoring
- Email domain checking
- Scam phrase detection

### What Won't Work:
- OCR processing (no Tesseract)
- Advanced NLP analysis (no spaCy)
- PDF parsing (no PyMuPDF)
- Image processing (no OpenCV)
- External API calls (no keys)

## Deployment Commands

### Render Backend:
```bash
git add .
git commit -m "Optimize for hosting"
git push origin main
```

### Vercel Frontend:
```bash
cd frontend
npm run build
vercel --prod
```

## Post-Deployment Steps

1. **Test the deployment**
2. **Add API keys** in dashboard
3. **Configure custom domain** (optional)
4. **Monitor usage** and upgrade if needed

## Upgrade Path

When you're ready for full features:
1. Upgrade to paid plan
2. Switch back to full requirements.txt
3. Add all API keys
4. Deploy full version

This approach ensures your app works immediately on free hosting while leaving room to upgrade later.
