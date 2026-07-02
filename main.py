import os
import re
import time
import math
import urllib.request
import urllib.parse
import json
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import nltk
from nltk.stem import WordNetLemmatizer


# Global variable for model parameters JSON
model_data = None
FACT_CHECK_API_KEY = "AIzaSyAFJufg3V5ArJrzxDFhxWzNDR_I0-Fzhh8"
NEWS_API_KEY = "1fa513057c4d4684887264914f35d197"

# Setup NLTK search path for local WordNet corpus
base_dir = os.path.dirname(os.path.abspath(__file__))
nltk.data.path.append(os.path.join(base_dir, "nltk_data"))
lemmatizer = WordNetLemmatizer()


# Identical STOPWORDS definition to ensure training and inference consistency
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
    """
    Identical text cleaning routine used in training to normalize inputs,
    apply WordNet lemmatization, and eliminate data leakage metrics (such as the Reuters bias).
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Convert to lowercase
    text = text.lower()
    
    # 2. Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # 3. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # 4. Remove publisher source markers to eliminate model leakage (Reuters bias)
    text = re.sub(r'\b(reuters|ap|associated\s+press|editorial)\b', '', text)
    
    # 5. Remove punctuation and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # 6. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 7. Remove stop words & Apply lemmatization
    words = text.split()
    cleaned_words = []
    for w in words:
        if w not in STOPWORDS:
            cleaned_words.append(lemmatizer.lemmatize(w))
            
    return " ".join(cleaned_words)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle startup and shutdown events.
    Loads the trained model parameters from model_data.json.
    """
    global model_data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "model_data.json")
    
    if not os.path.exists(model_path):
        print(f"CRITICAL ERROR: Model parameters JSON ('{model_path}') not found!")
    else:
        try:
            with open(model_path, "r") as f:
                model_data = json.load(f)
            print("SUCCESS: Pure Python model parameters loaded successfully!")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to load model parameters: {str(e)}")
            
    yield
    print("Application shutdown complete.")

app = FastAPI(
    title="VeriTruth AI - Fake News Detection API",
    description="FastAPI service utilizing a pure Python Logistic Regression model and Google Fact Check cross-referencing.",
    version="1.5.0",
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
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VeriTruthAI/1.5"}
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

def predict_pure_python(text: str):
    """
    Pure Python implementation of TF-IDF Vectorization and Logistic Regression.
    Eliminates dependency on heavy C-extension libraries like scikit-learn, numpy, and scipy.
    """
    global model_data
    
    # Load on-demand if serverless lifespans are skipped (common on Vercel boots)
    if model_data is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "model_data.json")
        try:
            with open(model_path, "r") as f:
                model_data = json.load(f)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Model parameters not found or failed to load: {str(e)}"
            )
            
    vocabulary = model_data["vocabulary"]
    idf = model_data["idf"]
    coef = model_data["coef"]
    intercept = model_data["intercept"]
    
    # 1. Clean the text using the exact same clean_text function
    cleaned = clean_text(text)
    
    # 2. Tokenize (matching Sklearn's default tokenizer regex pattern: (?u)\b\w\w+\b)
    words = re.findall(r'\b\w\w+\b', cleaned.lower())
    unigrams = words
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    tokens = unigrams + bigrams
    
    # 3. Calculate Term Frequencies (raw counts)
    tf_counts = {}
    for t in tokens:
        if t in vocabulary:
            tf_counts[t] = tf_counts.get(t, 0) + 1
            
    # 4. If no tokens match the vocabulary, predict using the default intercept sigmoid probability
    if not tf_counts:
        # z = intercept (since all tf_idf values are 0)
        prob_fake = 1 / (1 + math.exp(-intercept))
        prob_real = 1 - prob_fake
        verdict = "Fake" if prob_fake >= 0.5 else "Real"
        confidence = prob_fake if verdict == "Fake" else prob_real
        return verdict, confidence, {
            "Real": prob_real,
            "Fake": prob_fake
        }
        
    # 5. Multiply by IDF to get raw TF-IDF values
    tf_idf_raw = {}
    for term, count in tf_counts.items():
        idx = vocabulary[term]
        tf_idf_raw[idx] = count * idf[idx]
        
    # 6. Apply L2 normalization to match TfidfVectorizer output format
    sum_squares = sum(val ** 2 for val in tf_idf_raw.values())
    l2_norm = math.sqrt(sum_squares)
    
    tf_idf_norm = {}
    for idx, val in tf_idf_raw.items():
        tf_idf_norm[idx] = val / l2_norm
        
    # 7. Compute decision boundary: z = sum(coef[i] * tf_idf[i]) + intercept
    z = sum(coef[idx] * val for idx, val in tf_idf_norm.items()) + intercept
    
    # 8. Apply Sigmoid to get probability of Fake class (Class 1)
    prob_fake = 1 / (1 + math.exp(-z))
    prob_real = 1 - prob_fake
    
    verdict = "Fake" if prob_fake >= 0.5 else "Real"
    confidence = prob_fake if verdict == "Fake" else prob_real
    
    return verdict, confidence, {
        "Real": prob_real,
        "Fake": prob_fake
    }

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
@app.post("/api/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_article(request: PredictionRequest):
    """
    Predicts whether a news article is Real or Fake based on text structure.
    Also queries the Google Fact Check API to cross-reference known claims.
    """
    start_time = time.time()
    
    try:
        # Run classification in pure Python (no sklearn required)
        verdict, confidence, probabilities_map = predict_pure_python(request.text)
        
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

@app.get("/api/news", status_code=status.HTTP_200_OK)
async def get_latest_news(q: Optional[str] = None, category: Optional[str] = None):
    """
    Fetches latest news from NewsAPI, acting as a secure server-side proxy
    to bypass browser CORS policy restrictions on client keys.
    """
    try:
        if not q and not category:
            category = "general"
            
        if q:
            # Query everything endpoint for custom search keywords
            quoted_q = urllib.parse.quote(q)
            url = f"https://newsapi.org/v2/everything?q={quoted_q}&language=en&pageSize=12&apiKey={NEWS_API_KEY}"
        else:
            # Query top headlines for categories
            category_param = f"&category={category}" if category else ""
            url = f"https://newsapi.org/v2/top-headlines?country=us{category_param}&pageSize=12&apiKey={NEWS_API_KEY}"
            
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VeriTruthAI/1.5"}
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
    is_model_ready = model_data is not None
    return {
        "status": "online" if is_model_ready else "degraded",
        "model_loaded": is_model_ready
    }
