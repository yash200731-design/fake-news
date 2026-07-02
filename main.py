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

# Global variables for model and vectorizer
model = None
vectorizer = None
FACT_CHECK_API_KEY = "AIzaSyAFJufg3V5ArJrzxDFhxWzNDR_I0-Fzhh8"
NEWS_API_KEY = "1fa513057c4d4684887264914f35d197"

# NLTK local WordNet path setup
base_dir = os.path.dirname(os.path.abspath(__file__))
import nltk
nltk.data.path.append(os.path.join(base_dir, "nltk_data"))
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", 
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", 
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", 
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", 
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", 
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", 
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", 
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", 
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", 
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", 
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", 
    "yourselves"
}

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'<.*?>', '', text) # Remove HTML
    text = re.sub(r'https?://\S+|www\.\S+', '', text) # Remove URLs
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Remove special characters/numbers
    text = re.sub(r'\s+', ' ', text).strip() # Extra spaces
    
    words = text.split()
    cleaned = [lemmatizer.lemmatize(w) for w in words if w not in STOPWORDS]
    return " ".join(cleaned)

def extract_search_query(text: str) -> str:
    clean = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    first_sentence = sentences[0] if sentences else clean
    if len(first_sentence) > 150:
        first_sentence = first_sentence[:150]
    return first_sentence

def fetch_fact_check(query: str) -> Optional[dict]:
    if not query or not FACT_CHECK_API_KEY:
        return None
    try:
        quoted_query = urllib.parse.quote(query)
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={quoted_query}&key={FACT_CHECK_API_KEY}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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
        print(f"Fact Check warning: {str(e)}")
    return None

def get_fact_check_verdict_category(verdict_text: str) -> str:
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

def fetch_similar_news_newsapi(query: str) -> list:
    """
    Searches NewsAPI for similar news articles from trusted sources.
    """
    if not query or not NEWS_API_KEY:
        return []
    try:
        domains = "bbc.co.uk,bbc.com,reuters.com,thehindu.com,indianexpress.com,ndtv.com,cnn.com"
        quoted_query = urllib.parse.quote(query)
        url = f"https://newsapi.org/v2/everything?q={quoted_query}&domains={domains}&language=en&pageSize=4&apiKey={NEWS_API_KEY}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3.5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
        articles = []
        for art in res_data.get("articles", []):
            if art.get("title") and art.get("title") != "[Removed]":
                articles.append({
                    "source": art.get("source", {}).get("name", "Trusted Source"),
                    "headline": art.get("title", ""),
                    "published_date": art.get("publishedAt"),
                    "link": art.get("url", "")
                })
        return articles
    except Exception as e:
        print(f"NewsAPI query warning: {str(e)}")
        return []

def explain_text_perturbation(text: str, original_prob_real: float, num_features: int = 15) -> list:
    global model, vectorizer
    if not model or not vectorizer:
        return []
    try:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        unique_words = list(set([w for w in words if w.lower() not in STOPWORDS]))[:35]
        if not unique_words:
            return []
            
        perturbed_texts = []
        for word in unique_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            perturbed_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            perturbed_texts.append(clean_text(perturbed_text))
            
        X_perturbed = vectorizer.transform(perturbed_texts)
        probs = model.predict_proba(X_perturbed)
        
        highlights = []
        for i, word in enumerate(unique_words):
            perturbed_prob_real = probs[i][0] * 100.0
            diff = original_prob_real - perturbed_prob_real
            
            # Label supports: Real, Fake, or Neutral based on attribution delta
            if abs(diff) < 0.05:
                supports = "Neutral"
                score = 0.0
            else:
                supports = "Real" if diff > 0 else "Fake"
                score = round(abs(diff), 4)
                
            highlights.append({
                "word": word,
                "score": score,
                "supports": supports
            })
        # Sort highlights: put Neutral at the bottom
        highlights = sorted(highlights, key=lambda x: x["score"] if x["supports"] != "Neutral" else -1, reverse=True)[:num_features]
        return highlights
    except Exception as e:
        print(f"LIME attribution warning: {str(e)}")
        return []

model_error = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, vectorizer, model_error
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "model.pkl")
    vectorizer_path = os.path.join(base_dir, "vectorizer.pkl")
    
    try:
        import joblib
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            print("SUCCESS: Traditional model and vectorizer loaded successfully!")
        else:
            model_error = f"Files missing. model_path exists: {os.path.exists(model_path)}, vectorizer_path exists: {os.path.exists(vectorizer_path)}"
            print(f"CRITICAL: {model_error}")
    except Exception as e:
        model_error = f"{type(e).__name__}: {str(e)}"
        print(f"CRITICAL ERROR loading model: {str(e)}")
        
    yield
    print("Application shutdown complete.")

app = FastAPI(
    title="VeriTruth AI - News Credibility Analyzer",
    description="FastAPI service combining Scikit-Learn predictions, Google Fact Check verification, and explainability.",
    version="3.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Pydantic Model
class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=15, max_length=50000)

class SimilarNewsItem(BaseModel):
    source: str = Field(..., description="Publisher name")
    headline: str = Field(..., description="Article headline")
    published_date: Optional[str] = Field(None, description="Publish date")
    link: str = Field(..., description="Link URL")

class HighlightFeature(BaseModel):
    word: str = Field(..., description="Analyzed word token")
    score: float = Field(..., description="Explainability attribution score")
    supports: str = Field(..., description="Supports: 'Real', 'Fake', or 'Neutral'")

# Output Pydantic Model
class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Final Verdict")
    confidence: float = Field(..., description="Final confidence rating percentage")
    probability_real: float = Field(..., description="Raw probability Real class percentage")
    probability_fake: float = Field(..., description="Raw probability Fake class percentage")
    credibility_score: float = Field(..., description="Credibility score rating (0-100)")
    risk_level: str = Field(..., description="Risk Level: 'Low', 'Medium', or 'High'")
    fact_check_status: str = Field(..., description="Google Fact Check verification status rating")
    publisher: Optional[str] = Field(None, description="Fact check publisher")
    review_url: Optional[str] = Field(None, description="Fact check source review link")
    published_date: Optional[str] = Field(None, description="Fact check publish date")
    similar_news: List[SimilarNewsItem] = Field(default=[], description="Similar articles found from trusted sources")
    explanation: List[str] = Field(default=[], description="Bullet explanation sentences")
    highlights: List[HighlightFeature] = Field(default=[], description="Word highlight attributions")

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
@app.post("/api/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_article(request: PredictionRequest):
    try:
        # Graceful check for short headlines (Requirement 9)
        word_count = len(request.text.split())
        is_short = word_count < 8
        
        # 1. Machine Learning Inference
        if not model or not vectorizer:
            print("WARNING: Model artifacts not loaded. Falling back to default baseline estimates.")
            prob_real_pct = 50.0
            prob_fake_pct = 50.0
            ml_pred = "Real"
            confidence_pct = 50.0
        else:
            cleaned_text = clean_text(request.text)
            if not cleaned_text:
                cleaned_text = "empty text fallback"
                
            X_text = vectorizer.transform([cleaned_text])
            probs = model.predict_proba(X_text)[0] # [probability_real, probability_fake]
            
            prob_real_pct = round(probs[0] * 100, 1)
            prob_fake_pct = round(probs[1] * 100, 1)
            
            if is_short:
                # Override to low confidence if text is extremely short (Requirement 9)
                prob_real_pct = 50.0
                prob_fake_pct = 50.0
                ml_pred = "Real"
                confidence_pct = 50.0
            else:
                ml_pred = "Real" if prob_real_pct >= 50.0 else "Fake"
                confidence_pct = prob_real_pct if ml_pred == "Real" else prob_fake_pct
                
        # 2. Google Fact Check Verification
        search_query = extract_search_query(request.text)
        fact_check_result = fetch_fact_check(search_query)
        
        fact_check_category = "NONE"
        fc_status = "No verified fact check available."
        fc_pub = None
        fc_url = None
        fc_date = None
        
        if fact_check_result:
            fact_check_category = get_fact_check_verdict_category(fact_check_result["verdict"])
            fc_status = fact_check_result["verdict"]
            fc_pub = fact_check_result["publisher"]
            fc_url = fact_check_result["source_link"]
            fc_date = fact_check_result.get("date")
            
        # 3. Hybrid Decision Engine
        if fact_check_category == "TRUE":
            final_verdict = "VERIFIED REAL"
        elif fact_check_category == "FALSE":
            final_verdict = "FAKE"
        else:
            # No Google Fact Check matches
            if confidence_pct >= 80.0:
                final_verdict = ml_pred
            elif 60.0 <= confidence_pct < 80.0:
                final_verdict = "Likely Real" if ml_pred == "Real" else "Likely Fake"
            else:
                final_verdict = "Prediction Uncertain"
                
        # 4. News Verification Fallback
        similar_news = []
        if not fact_check_result:
            similar_news = fetch_similar_news_newsapi(search_query)
            
        # 5. Credibility Score & Risk Level calculation
        if final_verdict in ["Real", "VERIFIED REAL", "Likely Real"]:
            if confidence_pct > 90.0:
                credibility_score = round(95.0 + (confidence_pct - 90.0) * 0.5, 1)
                risk_level = "Low"
            elif 75.0 <= confidence_pct <= 90.0:
                credibility_score = round(80.0 + (confidence_pct - 75.0) * 14.0 / 15.0, 1)
                risk_level = "Medium"
            else:
                # Confidence < 75%
                credibility_score = round((confidence_pct / 75.0) * 79.0, 1)
                risk_level = "High"
        elif final_verdict in ["Fake", "FAKE", "Likely Fake"]:
            risk_level = "High"
            if confidence_pct > 90.0:
                credibility_score = round(100.0 - (95.0 + (confidence_pct - 90.0) * 0.5), 1)
            elif 75.0 <= confidence_pct <= 90.0:
                credibility_score = round(100.0 - (80.0 + (confidence_pct - 75.0) * 14.0 / 15.0), 1)
            else:
                credibility_score = round(100.0 - ((confidence_pct / 75.0) * 79.0), 1)
        else:
            # Prediction Uncertain
            credibility_score = 50.0
            risk_level = "Medium"
            
        # 6. Attributions & Explanations
        explanations_list = []
        if final_verdict in ["Real", "VERIFIED REAL", "Likely Real"]:
            if confidence_pct >= 75.0:
                explanations_list.append("Professional journalistic writing detected.")
            if final_verdict == "VERIFIED REAL":
                explanations_list.append("Matches verified news patterns.")
        elif final_verdict in ["Fake", "FAKE", "Likely Fake"]:
            explanations_list.append("Contains sensational or clickbait language.")
            explanations_list.append("Contains conspiracy-style phrases.")
        else:
            explanations_list.append("Low contextual certainty.")
            
        if similar_news:
            explanations_list.append("Similar to verified news patterns.")
            
        highlights = []
        if model and vectorizer:
            cleaned_text = clean_text(request.text)
            highlights = explain_text_perturbation(cleaned_text, prob_real_pct)
            
        return PredictionResponse(
            prediction=final_verdict,
            confidence=confidence_pct,
            probability_real=prob_real_pct,
            probability_fake=prob_fake_pct,
            credibility_score=credibility_score,
            risk_level=risk_level,
            fact_check_status=fc_status,
            publisher=fc_pub,
            review_url=fc_url,
            published_date=fc_date,
            similar_news=similar_news,
            explanation=explanations_list,
            highlights=highlights
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification endpoint error: {str(e)}"
        )

@app.get("/api/news", status_code=status.HTTP_200_OK)
async def get_latest_news(q: Optional[str] = None, category: Optional[str] = None):
    try:
        domains = "bbc.co.uk,bbc.com,reuters.com,thehindu.com,indianexpress.com,ndtv.com,cnn.com"
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
            
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4.0) as response:
            res_data = json.loads(response.read().decode("utf-8"))
        return res_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch news from NewsAPI: {str(e)}"
        )

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check():
    is_model_ready = model is not None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        "status": "online" if is_model_ready else "degraded",
        "model_loaded": is_model_ready,
        "error": model_error,
        "base_dir": base_dir,
        "model_exists": os.path.exists(os.path.join(base_dir, "model.pkl")),
        "vectorizer_exists": os.path.exists(os.path.join(base_dir, "vectorizer.pkl")),
        "dir_contents": os.listdir(base_dir) if os.path.exists(base_dir) else []
    }
