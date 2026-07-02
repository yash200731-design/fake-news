import os
import re
import time
import pandas as pd
import numpy as np
import joblib
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

# Setup NLTK search path
base_dir = os.path.dirname(os.path.abspath(__file__))
nltk.data.path.append(os.path.join(base_dir, "nltk_data"))

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

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'<.*?>', '', text) # HTML
    text = re.sub(r'https?://\S+|www\.\S+', '', text) # URLs
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Special chars & numbers
    text = re.sub(r'\s+', ' ', text).strip() # Extra spaces
    
    words = text.split()
    cleaned = [lemmatizer.lemmatize(w) for w in words if w not in STOPWORDS]
    return " ".join(cleaned)

def main():
    print("Loading True.csv and Fake.csv...")
    true_df = pd.read_csv('true.csv')
    fake_df = pd.read_csv('fake.csv')
    
    # Map labels: Real -> 0, Fake -> 1
    true_df['label'] = 0
    fake_df['label'] = 1
    
    df = pd.concat([true_df, fake_df], ignore_index=True)
    
    print(f"Total articles: {len(df)}")
    
    # Remove duplicate records
    df.drop_duplicates(subset=['text'], keep='first', inplace=True)
    print(f"Deduplicated articles: {len(df)}")
    
    # Combine title and text
    df['combined'] = df['title'] + " " + df['text']
    
    # Balance classes
    fake_subset = df[df['label'] == 1]
    real_subset = df[df['label'] == 0]
    min_size = min(len(fake_subset), len(real_subset))
    
    # Sample down to 3000 balanced articles per class (6000 total) for fast CPU training
    sample_size = min(3000, min_size)
    print(f"Sampling {sample_size * 2} articles for balanced grid search & final training...")
    fake_balanced = fake_subset.sample(n=sample_size, random_state=42)
    real_balanced = real_subset.sample(n=sample_size, random_state=42)
    
    df_balanced = pd.concat([fake_balanced, real_balanced], ignore_index=True)
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("Preprocessing text...")
    df_balanced['cleaned'] = df_balanced['combined'].apply(clean_text)
    
    # Train-val-test split (80/10/10)
    train_df, temp_df = train_test_split(df_balanced, test_size=0.2, random_state=42, stratify=df_balanced['label'])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label'])
    
    # Vectorizer
    print("Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(max_features=50000, ngram_range=(1,2), min_df=2, max_df=0.9)
    X_train = vectorizer.fit_transform(train_df['cleaned'])
    y_train = train_df['label'].values
    
    X_val = vectorizer.transform(val_df['cleaned'])
    y_val = val_df['label'].values
    
    X_test = vectorizer.transform(test_df['cleaned'])
    y_test = test_df['label'].values
    
    print("Tuning Logistic Regression...")
    lr_grid = GridSearchCV(LogisticRegression(max_iter=1000, random_state=42), {'C': [0.1, 1.0, 10.0]}, cv=3, scoring='accuracy')
    lr_grid.fit(X_train, y_train)
    best_lr = lr_grid.best_estimator_
    
    print("Tuning Linear SVM...")
    svm_grid = GridSearchCV(LinearSVC(max_iter=2000, random_state=42, dual=False), {'C': [0.1, 1.0, 10.0]}, cv=3, scoring='accuracy')
    svm_grid.fit(X_train, y_train)
    best_svm_base = svm_grid.best_estimator_
    
    # Wrap base SVM in CalibratedClassifierCV to support predict_proba
    calibrated_svm = CalibratedClassifierCV(best_svm_base, cv=3)
    calibrated_svm.fit(X_train, y_train)
    
    print("Tuning Random Forest...")
    rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), {'n_estimators': [50, 100], 'max_depth': [20, None]}, cv=3, scoring='accuracy')
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_
    
    models = {
        "Logistic Regression": best_lr,
        "Linear SVM (Calibrated)": calibrated_svm,
        "Random Forest": best_rf
    }
    
    best_model_name = None
    best_model_obj = None
    best_accuracy = -1
    
    print("\n--- Model Evaluation on Test Set ---")
    for name, model_obj in models.items():
        preds = model_obj.predict(X_test)
        probs = model_obj.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds)
        rec = recall_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        auc = roc_auc_score(y_test, probs)
        cm = confusion_matrix(y_test, preds)
        
        print(f"\nModel: {name}")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1-score:  {f1:.4f}")
        print(f"  ROC-AUC:   {auc:.4f}")
        print("  Confusion Matrix:")
        print(cm)
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model_obj = model_obj
            
    print(f"\nBest Model: {best_model_name} with Accuracy: {best_accuracy:.4f}")
    
    # Save best model and vectorizer
    joblib.dump(best_model_obj, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    print("SUCCESS: model.pkl and vectorizer.pkl saved successfully!")

if __name__ == "__main__":
    main()
