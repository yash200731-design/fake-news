import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib

# Global variables for model artifacts
model = None
vectorizer = None

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
    # Clean up at shutdown (if needed)
    print("Application shutdown complete.")

app = FastAPI(
    title="VeriTruth AI - Fake News Detection API",
    description="FastAPI service utilizing a Scikit-Learn Logistic Regression model and TF-IDF Vectorizer to classify articles as Real or Fake.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Vite dev server (and any other domain) to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
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

# Output Pydantic Model for API response validation
class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Legitimacy verdict: 'Real' or 'Fake'")
    confidence: float = Field(..., description="Model confidence score as a fraction (0.0 to 1.0)")
    probabilities: dict = Field(..., description="Probability scores for each class")
    processing_time: float = Field(..., description="Server classification execution time in seconds")

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
@app.post("/api/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_article(request: PredictionRequest):
    """
    Predicts whether a news article is Real or Fake based on text structure.
    Accepts JSON body: {"text": "..."}
    Returns prediction verdict, confidence score, probabilities, and execution timing.
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
        
        processing_duration = round(time.time() - start_time, 4)
        
        return PredictionResponse(
            prediction=verdict,
            confidence=confidence,
            probabilities=probabilities_map,
            processing_time=processing_duration
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
