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
import joblib

# Global variables for model artifacts
model = None
vectorizer = None
FACT_CHECK_API_KEY = "AIzaSyAFJufg3V5ArJrzxDFhxWzNDR_I0-Fzhh8"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle startup and shutdown events.
    Loads the trained model and vectorizer at application startup.
    """
    global model, vectorizer
    model_path = "model.pkl"
    vectorizer_path = "vectorizer.pkl"
    
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        print(f"CRITICAL ERROR: Model artifacts ('{model_path}', '{vectorizer_path}') not found!")
        print("Please execute 'python train_model.py' to train and export the model artifacts first.")
    else:
        try:
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            print("SUCCESS: Machine learning model and TF-IDF vectorizer loaded successfully!")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to load model artifacts: {str(e)}")
            
    yield
    print("Application shutdown complete.")

app = FastAPI(
    title="VeriTruth AI - Fake News Detection API",
    description="FastAPI service utilizing a Scikit-Learn Logistic Regression model and Google Fact Check cross-referencing.",
    version="1.3.0",
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
        description="The full content of the news article to predict.",
        examples=["Researchers published a new peer-reviewed study on Wednesday..."]
    )

# Fact-Check Details Pydantic Model
class FactCheckInfo(BaseModel):
    claim_title: str = Field(..., description="The reviewed claim title returned by Google Fact Check.")
    verdict: str = Field(..., description="The fact-check rating/verdict.")
    publisher: str = Field(..., description="Fact-checking publisher name.")
    date: Optional[str] = Field(None, description="Date of the claim review.")
    source_link: str = Field(..., description="URL to the claim review source article.")

# Output Pydantic Model for API response validation
class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Legitimacy verdict: 'Real' or 'Fake'")
    confidence: float = Field(..., description="Model confidence score as a fraction (0.0 to 1.0)")
    probabilities: dict = Field(..., description="Probability scores for each class")
    processing_time: float = Field(..., description="Server classification execution time in seconds")
    fact_check: Optional[FactCheckInfo] = Field(None, description="Google Fact Check matches (if found)")

def extract_search_query(text: str) -> str:
    """
    Extracts a short, concise search query from the news text
    by stripping clickbait headers and grabbing the first sentence.
    """
    clean = re.sub(r'\s+', ' ', text).strip()
    
    # Strip common clickbait prefixes at the start
    prefixes = [
        r'^warning:\s*', r'^breaking news:\s*', r'^breaking:\s*', 
        r'^shocking truth:\s*', r'^must read:\s*', r'^alert:\s*', 
        r'^anonymous source claims:\s*', r'^miracle cure exposed:\s*',
        r'^miracle cure:\s*', r'^revealed:\s*', r'^alert:\s*'
    ]
    for pattern in prefixes:
        clean = re.sub(pattern, '', clean, flags=re.IGNORECASE)
        
    sentences = re.split(r'[.!?]\s+', clean)
    if sentences:
        first_sentence = sentences[0].strip()
        if len(first_sentence) > 110:
            return first_sentence[:107] + "..."
        return first_sentence
    return clean[:110]

def extract_keywords(text: str) -> str:
    """
    Extracts the first 4 key search terms (excluding stop words, clickbait phrases,
    and common auxiliary verbs) to perform a semantic fallback search.
    """
    words = re.findall(r'\b[a-zA-Z0-9-]+\b', text.lower())
    stop_words = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at",
        "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "did", "do",
        "does", "doing", "don", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have",
        "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into",
        "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off",
        "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
        "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
        "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
        "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with", "you", "your",
        "yours", "yourself", "yourselves", "warning", "breaking", "news", "alert", "shocking", "truth", "secret", "source",
        "will", "would", "shall", "should", "must", "can", "could", "may", "might", "involve", "involving", "involved",
        "implant", "implanting", "implanted", "under", "over", "above", "below", "during", "within", "without",
        "against", "about", "into", "onto", "upon", "across", "along", "around", "before", "after", "between",
        "among", "throughout", "towards", "by", "of", "off", "out", "up", "down", "again", "further", "then", "once"
    }
    keywords = [w for w in words if w not in stop_words]
    return " ".join(keywords[:4])

def fetch_fact_check(query: str) -> Optional[dict]:
    """
    Queries Google Fact Check Tools API to find matching verified claims.
    Employs a 2.5-second connection timeout for reliability.
    """
    if not query:
        return None
    try:
        quoted_query = urllib.parse.quote(query)
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={quoted_query}&key={FACT_CHECK_API_KEY}"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VeriTruthAI/1.3"}
        )
        
        with urllib.request.urlopen(req, timeout=2.5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
        claims = res_data.get("claims", [])
        if not claims:
            return None
            
        claim = claims[0]
        claim_reviews = claim.get("claimReview", [])
        if not claim_reviews:
            return None
            
        review = claim_reviews[0]
        
        return {
            "claim_title": claim.get("text", "Unknown Claim"),
            "verdict": review.get("textualRating", "No Verdict"),
            "publisher": review.get("publisher", {}).get("name", "Unknown Publisher"),
            "date": review.get("reviewDate") or claim.get("claimDate"),
            "source_link": review.get("url", "#")
        }
    except Exception as e:
        print(f"WARNING: Google Fact Check Tools API lookup failed or timed out: {str(e)}")
        return None

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
@app.post("/api/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_article(request: PredictionRequest):
    """
    Predicts whether a news article is Real or Fake based on text structure.
    Also queries the Google Fact Check API to cross-reference known claims.
    """
    global model, vectorizer
    
    # Verify that model artifacts are loaded
    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Please train the model or check server configurations."
        )
        
    start_time = time.time()
    
    try:
        # Preprocess and vectorise input text
        text_vector = vectorizer.transform([request.text])
        
        # Predict class index (0 = Real, 1 = Fake)
        pred_class_idx = int(model.predict(text_vector)[0])
        
        # Predict class probabilities
        probs = model.predict_proba(text_vector)[0]
        
        # Map values
        verdict = "Real" if pred_class_idx == 0 else "Fake"
        confidence = float(probs[pred_class_idx])
        probabilities_map = {
            "Real": float(probs[0]),
            "Fake": float(probs[1])
        }
        
        # Extract search query and lookup Google Fact Check API
        search_query = extract_search_query(request.text)
        fact_check_result = fetch_fact_check(search_query)
        
        # Fallback if first sentence fails
        if not fact_check_result:
            keywords_query = extract_keywords(search_query)
            if keywords_query:
                fact_check_result = fetch_fact_check(keywords_query)
        
        processing_duration = round(time.time() - start_time, 4)
        
        fact_check_info = None
        if fact_check_result:
            fact_check_info = FactCheckInfo(
                claim_title=fact_check_result["claim_title"],
                verdict=fact_check_result["verdict"],
                publisher=fact_check_result["publisher"],
                date=fact_check_result.get("date"),
                source_link=fact_check_result["source_link"]
            )
        
        return PredictionResponse(
            prediction=verdict,
            confidence=confidence,
            probabilities=probabilities_map,
            processing_time=processing_duration,
            fact_check=fact_check_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal classification failed: {str(e)}"
        )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify server status and model loading.
    """
    is_model_ready = model is not None and vectorizer is not None
    return {
        "status": "online" if is_model_ready else "degraded",
        "model_loaded": is_model_ready
    }
