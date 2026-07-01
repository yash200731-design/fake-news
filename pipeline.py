import re
import time
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Custom English stop words list to avoid NLTK download overhead and offline errors
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

def clean_text(text):
    """
    Cleans the input news text by removing tags, URLs, source headers, stop words,
    and lowercasing all words.
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
    
    # 5. Remove special characters and digits, leaving only letters and spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # 6. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 7. Remove stop words
    words = text.split()
    cleaned_words = [word for word in words if word not in STOPWORDS]
    
    return " ".join(cleaned_words)

def main():
    print("--------------------------------------------------")
    print("VeriTruth ML Pipeline: Kaggle Fake/Real News Setup")
    print("--------------------------------------------------")
    
    start_time = time.time()
    
    # 1. Load Datasets
    try:
        print("[1/6] Loading true.csv and fake.csv...")
        true_df = pd.read_csv('true.csv')
        fake_df = pd.read_csv('fake.csv')
    except FileNotFoundError as e:
        print("ERROR: Kaggle CSV datasets not found in the current directory.")
        print("Please run 'python generate_datasets.py' to simulate datasets first.")
        return
        
    # 2. Merge and Label Datasets (0 = Real, 1 = Fake)
    print(f"[2/6] Merging datasets. True rows: {len(true_df)}, Fake rows: {len(fake_df)}")
    true_df['class'] = 0
    fake_df['class'] = 1
    
    # Merge
    df = pd.concat([true_df, fake_df], ignore_index=True)
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # 3. Clean Text and Remove Stop Words
    print("[3/6] Preprocessing and cleaning article text...")
    # Clean the 'text' field (or combine title + text for better features)
    df['clean_text'] = df['text'].apply(clean_text)
    
    # 4. Apply TF-IDF Vectorizer
    print("[4/6] Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(max_features=2500, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df['clean_text'])
    y = df['class']
    
    # 5. Train Logistic Regression Model
    print("[5/6] Splitting data and training Logistic Regression model...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = LogisticRegression(C=1.0, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Display Metrics
    print("\n---------------- MODEL METRICS ----------------")
    print(f"Accuracy:  {accuracy:.4f} (percentage of correct predictions)")
    print(f"Precision: {precision:.4f} (ratio of true positives to all positive predictions)")
    print(f"Recall:    {recall:.4f} (ratio of true positives to actual positives)")
    print(f"F1-Score:  {f1:.4f} (harmonic mean of precision and recall)")
    print("-----------------------------------------------\n")
    
    # 6. Save model.pkl and vectorizer.pkl
    print("[6/6] Serializing and saving model artifacts...")
    joblib.dump(model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    
    duration = time.time() - start_time
    print(f"SUCCESS: Pipeline completed in {duration:.2f} seconds!")
    print("Artifacts 'model.pkl' and 'vectorizer.pkl' updated successfully.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
