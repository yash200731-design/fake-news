import os
import re
import time
import urllib.request
import urllib.parse
import json
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Global variables for model and tokenizer
tokenizer = None
model = None
FACT_CHECK_API_KEY = "AIzaSyAFJufg3V5ArJrzxDFhxWzNDR_I0-Fzhh8"
NEWS_API_KEY = "1fa513057c4d4684887264914f35d197"

def clean_text_bert(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_search_query(text: str) -> str:
    """
    Extracts the main claim sentence from the article text for fact check lookup.
    """
    clean = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    first_sentence = sentences[0] if sentences else clean
    if len(first_sentence) > 150:
        first_sentence = first_sentence[:150]
    return first_sentence

def fetch_fact_check(query: str) -> Optional[dict]:
    """
    Queries Google Fact Check Tools API for the given search query.
    """
    if not query or not FACT_CHECK_API_KEY:
        return None
    try:
        quoted_query = urllib.parse.quote(query)
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={quoted_query}&key={FACT_CHECK_API_KEY}"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VeriTruthAI/2.1"}
        )
        
        with urllib.request.urlopen(req, timeout=3.5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
        if res_data.get("claims"):
            claim = res_data["claims"][0]
            if claim.get("claimReview"):
                review = claim["claimReview"][0]
                return {
                    "verdict": review.get("textualRating", "Unknown"),
                    "publisher": review.get("publisher", {}).get("name", "Unknown"),
                    "date": review.get("reviewDate"),
                    "source_link": review.get("url")
                }
    except Exception as e:
        print(f"Fact Check API warning: {str(e)}")
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle startup and shutdown events.
    Loads the fine-tuned DistilBERT model. If the local weights are missing
    (e.g., on Vercel deployment), it falls back to the default distilbert-base-uncased weights.
    """
    global tokenizer, model
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "best_model")
    
    model_path = model_dir if os.path.exists(model_dir) else "distilbert-base-uncased"
    print(f"Loading DistilBERT model and tokenizer from: {model_path}")
    
    try:
        import torch
        from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
        tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
        model = DistilBertForSequenceClassification.from_pretrained(model_path)
        model.eval()
        print("SUCCESS: DistilBERT model loaded successfully!")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to load DistilBERT model: {str(e)}")
        
    yield
    print("Application shutdown complete.")

app = FastAPI(
    title="VeriTruth AI - Fake News Detection API",
    description="FastAPI service utilizing a Hugging Face DistilBERT Transformer fake news classifier and Google Fact Check API.",
    version="2.1.0",
    lifespan=lifespan
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Pydantic Model for API request validation
class PredictionRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=15, 
        max_length=50000, 
        description="The full content of the news article to predict."
    )

# Output Pydantic Model for API response validation
class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Machine Learning Prediction: 'Real' or 'Fake'")
    confidence: float = Field(..., description="Model confidence score as a percentage (0.0 to 100.0)")
    fact_check_status: str = Field(..., description="Google Fact Check status verdict or 'No verified fact check found.'")
    publisher: Optional[str] = Field(None, description="Fact check publisher")
    review_url: Optional[str] = Field(None, description="URL of the fact check review")
    published_date: Optional[str] = Field(None, description="Published date of the claim review")

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
@app.post("/api/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_article(request: PredictionRequest):
    """
    Predicts whether a news article is Real or Fake using the fine-tuned DistilBERT model.
    Also queries the Google Fact Check API to cross-reference the claim.
    """
    try:
        cleaned_text = clean_text_bert(request.text)
        
        # 1. DistilBERT Prediction
        if not tokenizer or not model:
            print("WARNING: DistilBERT model not loaded. Falling back to default confidence response.")
            verdict = "Real"
            confidence_pct = 50.0
        else:
            import torch
            # Tokenize text
            inputs = tokenizer(cleaned_text, return_tensors="pt", truncation=True, max_length=256, padding=True)
            
            # Run inference
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                
            # Apply Softmax to get probabilities
            probs = torch.softmax(logits, dim=-1).squeeze().tolist()
            prob_real = probs[0]
            prob_fake = probs[1]
            
            verdict = "Real" if prob_real >= 0.5 else "Fake"
            confidence = prob_real if verdict == "Real" else prob_fake
            confidence_pct = round(confidence * 100, 1)
            
        # 2. Google Fact Check Verification
        search_query = extract_search_query(request.text)
        fact_check_result = fetch_fact_check(search_query)
        
        if fact_check_result:
            return PredictionResponse(
                prediction=verdict,
                confidence=confidence_pct,
                fact_check_status=fact_check_result["verdict"],
                publisher=fact_check_result["publisher"],
                review_url=fact_check_result["source_link"],
                published_date=fact_check_result.get("date")
            )
        else:
            return PredictionResponse(
                prediction=verdict,
                confidence=confidence_pct,
                fact_check_status="No verified fact check found.",
                publisher=None,
                review_url=None,
                published_date=None
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DistilBERT classification failed: {str(e)}"
        )

@app.get("/api/news", status_code=status.HTTP_200_OK)
async def get_latest_news(q: Optional[str] = None, category: Optional[str] = None):
    """
    Proxy route for NewsAPI queries.
    """
    try:
        if not q and not category:
            category = "general"
            
        if q:
            quoted_q = urllib.parse.quote(q)
            url = f"https://newsapi.org/v2/everything?q={quoted_q}&language=en&pageSize=12&apiKey={NEWS_API_KEY}"
        else:
            category_param = f"&category={category}" if category else ""
            url = f"https://newsapi.org/v2/top-headlines?country=us{category_param}&pageSize=12&apiKey={NEWS_API_KEY}"
            
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VeriTruthAI/2.1"}
        )
        
        with urllib.request.urlopen(req, timeout=4.0) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
        return res_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch news from NewsAPI: {str(e)}"
        )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify server status.
    """
    is_model_ready = model is not None
    return {
        "status": "online" if is_model_ready else "degraded",
        "model_loaded": is_model_ready
    }
