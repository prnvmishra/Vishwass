import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np

def preprocess_image(image_bytes: bytes) -> Image.Image:
    """Safely converts generic photos to grayscale. Skips invasive transformations for PDFs."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return Image.open(io.BytesIO(image_bytes))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return Image.fromarray(gray)
    except:
        return Image.open(io.BytesIO(image_bytes))

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a uploaded PDF file using dual engines and OCR fallback."""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber error: {e}")
        
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
            
        print(f"Omnidirectional Parser -> Native PyMuPDF Text Length: {len(text)}")
            
        # ALWAYS forcefully OCR the document (first 2 pages) to guarantee no embedded photos are missed!
        text += "\n\n--- DEEP OPTICAL CHARACTER RECOGNITION (OCR) SCAN ---\n"
        page_count = min(len(doc), 2)
        for i in range(page_count):
            pix = doc[i].get_pixmap(dpi=250)
            img_bytes = pix.tobytes("png")
            
            # Formally route through the OpenCV Preprocessor for optimal contrast
            img = preprocess_image(img_bytes)
            
            # Extract raw string from pixels
            text += pytesseract.image_to_string(img) + "\n"
            
        print(f"Omnidirectional Parser -> Final Combined Text Length: {len(text)}")
        
    except Exception as e:
        print(f"PyMuPDF/OCR error: {e}")
            
    return text.strip()

def extract_text_from_image(file_bytes: bytes) -> str:
    """Extracts text from an image using Tesseract OCR with OpenCV preprocessing."""
    text = ""
    try:
        img = preprocess_image(file_bytes)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error reading Image: {e}")
    return text.strip()

def parse_document(file_bytes: bytes, filename: str) -> str:
    """Router to parse based on file extension."""
    filename_lower = filename.lower()
    
    # Text fallback for hackathon demos
    if filename_lower.endswith(".txt") or filename_lower.endswith(".md"):
        try:
            return file_bytes.decode('utf-8')
        except:
            pass
            
    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith((".png", ".jpg", ".jpeg")):
        return extract_text_from_image(file_bytes)
    return ""
