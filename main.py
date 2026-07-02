import os
import re
import time
import urllib.request
import urllib.parse
import json
from contextlib import asynccontextmanager
from typing import Optional, List
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

def get_fact_check_verdict_category(verdict_text: str) -> str:
    """
    Classifies raw fact check ratings into FALSE, TRUE, or NONE categories.
    """
    if not verdict_text:
        return "NONE"
    v = verdict_text.lower()
    false_keywords = ["false", "fake", "incorrect", "untrue", "debunked", "misleading", "partly false"]
    true_keywords = ["true", "correct", "accurate", "legitimate", "verified", "mostly true", "correct attribution"]
    
    if any(fk in v for fk in false_keywords):
        return "FALSE"
    if any(tk in v for tk in true_keywords):
        return "TRUE"
    return "NONE"

def explain_text_lime(text: str, original_prob_real: float, num_features: int = 15) -> list:
    """
    Runs a lightweight LIME-like perturbation check to determine word importance.
    """
    global tokenizer, model
    if not tokenizer or not model:
        return []
        
    try:
        import torch
        # Clean and tokenize words of length >= 4
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        
        # Standard english stopwords list
        stopwords = {
            "the", "and", "a", "of", "to", "is", "in", "that", "it", "he", "was", "for", "on", 
            "are", "as", "with", "his", "they", "i", "at", "be", "this", "have", "from", "or", 
            "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", 
            "your", "can", "said", "there", "use", "an", "each", "which", "she", "do", "how", 
            "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", 
            "these", "so", "some", "her", "would", "make", "like", "him", "into", "time", 
            "has", "look", "two", "more", "write", "go", "see", "number", "no", "way", 
            "could", "people", "my", "than", "first", "water", "been", "call", "who", "oil", 
            "its", "now", "find", "long", "down", "day", "did", "get", "come", "made", "may", 
            "part", "news", "said", "also", "would", "about", "were"
        }
        
        unique_words = list(set([w for w in words if w.lower() not in stopwords]))[:30]
        if not unique_words:
            return []
            
        # Create perturbed variations of text
        perturbed_texts = []
        for word in unique_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            perturbed_text = re.sub(pattern, '[MASK]', text, flags=re.IGNORECASE)
            perturbed_texts.append(perturbed_text)
            
        # Batch inference
        inputs = tokenizer(perturbed_texts, return_tensors="pt", truncation=True, max_length=256, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            
        probs = torch.softmax(logits, dim=-1).tolist()
        
        highlights = []
        for i, word in enumerate(unique_words):
            perturbed_prob_real = probs[i][0]
            diff = original_prob_real - perturbed_prob_real
            
            if abs(diff) > 0.001:
                supports = "Real" if diff > 0 else "Fake"
                highlights.append({
                    "word": word,
                    "score": round(abs(diff), 4),
                    "supports": supports
                })
                
        # Sort by importance magnitude
        highlights = sorted(highlights, key=lambda x: x["score"], reverse=True)[:num_features]
        return highlights
    except Exception as e:
        print(f"LIME explainability warning: {str(e)}")
        return []

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
    description="FastAPI service utilizing a Hugging Face DistilBERT Transformer, Google Fact Check API, and LIME Explainability.",
    version="2.3.0",
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

class HighlightFeature(BaseModel):
    word: str = Field(..., description="The word analyzed")
    score: float = Field(..., description="Explainability attribution score")
    supports: str = Field(..., description="Class supported: 'Real' or 'Fake'")

# Output Pydantic Model for API response validation
class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Final Verdict")
    ml_prediction: str = Field(..., description="Raw Machine Learning Prediction")
    confidence: float = Field(..., description="Model confidence score")
    uncertain: bool = Field(..., description="True if final verdict is Prediction Uncertain")
    fact_check_status: str = Field(..., description="Google Fact Check Status")
    publisher: Optional[str] = Field(None, description="Fact check publisher")
    review_url: Optional[str] = Field(None, description="URL of the fact check review")
    published_date: Optional[str] = Field(None, description="Published date of the claim review")
    highlights: List[HighlightFeature] = Field(default=[], description="LIME explainability highlights")

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
@app.post("/api/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_article(request: PredictionRequest):
    """
    Predicts whether a news article is Real or Fake using the fine-tuned DistilBERT model.
    Includes Google Fact Check verification and LIME-like attribution explainability highlights.
    """
    try:
        cleaned_text = clean_text_bert(request.text)
        
        # 1. DistilBERT Prediction
        prob_real = 0.5
        prob_fake = 0.5
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
        
        # Classify the fact check rating if found
        fact_check_category = "NONE"
        if fact_check_result:
            fact_check_category = get_fact_check_verdict_category(fact_check_result["verdict"])
            
        # 3. Hybrid Decision Engine Precedence Rules
        if fact_check_category == "FALSE":
            final_verdict = "Fake"
            is_uncertain = False
        elif fact_check_category == "TRUE":
            final_verdict = "Verified Real"
            is_uncertain = False
        else:
            # Fact check has no result (NONE)
            if confidence_pct > 90.0:
                final_verdict = verdict
                is_uncertain = False
            else:
                final_verdict = "Prediction Uncertain"
                is_uncertain = True
                
        # 4. LIME Explainability Highlights
        highlights = []
        if tokenizer and model:
            highlights = explain_text_lime(cleaned_text, prob_real)
            
        # Format fact check response parameters
        fc_status = fact_check_result["verdict"] if fact_check_result else "No verified fact check found."
        fc_pub = fact_check_result["publisher"] if fact_check_result else None
        fc_url = fact_check_result["source_link"] if fact_check_result else None
        fc_date = fact_check_result.get("date") if fact_check_result else None
        
        return PredictionResponse(
            prediction=final_verdict,
            ml_prediction=verdict,
            confidence=confidence_pct,
            uncertain=is_uncertain,
            fact_check_status=fc_status,
            publisher=fc_pub,
            review_url=fc_url,
            published_date=fc_date,
            highlights=highlights
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DistilBERT classification failed: {str(e)}"
        )

@app.get("/api/news", status_code=status.HTTP_200_OK)
async def get_latest_news(q: Optional[str] = None, category: Optional[str] = None):
    """
    Proxy route for NewsAPI queries, restricted to BBC, Reuters, The Hindu, Indian Express, NDTV, and CNN.
    Supports keywords and category keyword filtering.
    """
    try:
        domains = "bbc.co.uk,bbc.com,reuters.com,thehindu.com,indianexpress.com,ndtv.com,cnn.com"
        
        # Build search query by combining q and category
        search_terms = []
        if q:
            search_terms.append(q)
        if category and category.lower() != 'all':
            search_terms.append(category)
            
        if search_terms:
            combined_q = " ".join(search_terms)
            quoted_q = urllib.parse.quote(combined_q)
            url = f"https://newsapi.org/v2/everything?q={quoted_q}&domains={domains}&language=en&pageSize=12&apiKey={NEWS_API_KEY}"
        else:
            url = f"https://newsapi.org/v2/everything?domains={domains}&language=en&sortBy=publishedAt&pageSize=12&apiKey={NEWS_API_KEY}"
            
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VeriTruthAI/2.2"}
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
