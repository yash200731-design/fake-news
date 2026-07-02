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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Setup NLTK search path for local WordNet corpus
base_dir = os.path.dirname(os.path.abspath(__file__))
nltk.data.path.append(os.path.join(base_dir, "nltk_data"))

# Initialize WordNet Lemmatizer
lemmatizer = WordNetLemmatizer()

# Standard stopword list matching main.py
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

def clean_and_lemmatize(text):
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
            # Lemmatize noun forms
            cleaned_words.append(lemmatizer.lemmatize(w))
            
    return " ".join(cleaned_words)

def main():
    print("Loading datasets...")
    # Read Kaggle CSV files
    true_df = pd.read_csv('true.csv')
    fake_df = pd.read_csv('fake.csv')

    # Assign labels (0 = Real, 1 = Fake)
    true_df['label'] = 0
    fake_df['label'] = 1

    # Combine datasets
    df = pd.concat([true_df, fake_df], ignore_index=True)
    print(f"Total articles loaded: {len(df)} (True: {len(true_df)}, Fake: {len(fake_df)})")

    # Combine title and text columns
    print("Combining title and text...")
    df['combined_text'] = df['title'] + " " + df['text']

    # Preprocess text
    print("Preprocessing, cleaning and lemmatizing text (this may take 1-2 minutes)...")
    start_time = time.time()
    df['cleaned_text'] = df['combined_text'].apply(clean_and_lemmatize)
    print(f"Preprocessing completed in {time.time() - start_time:.2f}s")

    # Split into train/test sets (80% train, 20% test)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

    # TF-IDF Feature Engineering
    print("Initializing TF-IDF vectorizer (max_features=50000)...")
    vectorizer = TfidfVectorizer(max_features=50000, ngram_range=(1, 2), min_df=2, max_df=0.9)
    
    print("Fitting vectorizer on training text...")
    X_train = vectorizer.fit_transform(train_df['cleaned_text'])
    y_train = train_df['label'].values
    
    print("Transforming test text...")
    X_test = vectorizer.transform(test_df['cleaned_text'])
    y_test = test_df['label'].values

    # Subsample for GridSearchCV hyperparameter tuning to keep training time reasonable
    print("Subsampling for hyperparameter tuning...")
    grid_sample_size = min(8000, len(train_df))
    grid_df = train_df.sample(n=grid_sample_size, random_state=42)
    X_grid = vectorizer.transform(grid_df['cleaned_text'])
    y_grid = grid_df['label'].values
    
    X_grid_train, X_grid_test, y_grid_train, y_grid_test = train_test_split(
        X_grid, y_grid, test_size=0.25, random_state=42, stratify=y_grid
    )

    print(f"Grid search tuning sample sizes: Train={X_grid_train.shape[0]}, Test={X_grid_test.shape[0]}")

    models_comparison = {}

    # 1. Tune Logistic Regression
    print("\nTuning Logistic Regression using GridSearchCV...")
    lr_param_grid = {'C': [0.1, 1.0, 10.0]}
    lr_grid = GridSearchCV(LogisticRegression(max_iter=1000, random_state=42), lr_param_grid, cv=3, n_jobs=-1, scoring='f1')
    lr_grid.fit(X_grid_train, y_grid_train)
    best_lr = lr_grid.best_estimator_
    print(f"Best Logistic Regression Params: {lr_grid.best_params_}")
    models_comparison['Logistic Regression'] = (best_lr, lr_grid.best_params_)

    # 2. Tune Linear SVM
    print("\nTuning Linear SVM using GridSearchCV...")
    svm_param_grid = {'C': [0.1, 1.0, 10.0]}
    svm_grid = GridSearchCV(LinearSVC(max_iter=2000, random_state=42, dual=False), svm_param_grid, cv=3, n_jobs=-1, scoring='f1')
    svm_grid.fit(X_grid_train, y_grid_train)
    best_svm = svm_grid.best_estimator_
    print(f"Best Linear SVM Params: {svm_grid.best_params_}")
    models_comparison['Linear SVM'] = (best_svm, svm_grid.best_params_)

    # 3. Tune Random Forest
    print("\nTuning Random Forest using GridSearchCV...")
    rf_param_grid = {'n_estimators': [50, 100], 'max_depth': [20, None]}
    rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_param_grid, cv=3, n_jobs=-1, scoring='f1')
    rf_grid.fit(X_grid_train, y_grid_train)
    best_rf = rf_grid.best_estimator_
    print(f"Best Random Forest Params: {rf_grid.best_params_}")
    models_comparison['Random Forest'] = (best_rf, rf_grid.best_params_)

    # Evaluate Tuned Models on validation subset
    best_model_name = None
    best_model_score = -1
    best_model_params = None

    print("\n--- Model Tuning Results (Subset Evaluation) ---")
    for name, (model_obj, params) in models_comparison.items():
        preds = model_obj.predict(X_grid_test)
        f1 = f1_score(y_grid_test, preds)
        acc = accuracy_score(y_grid_test, preds)
        print(f"{name}: F1-Score={f1:.4f}, Accuracy={acc:.4f} (Params: {params})")
        if f1 > best_model_score:
            best_model_score = f1
            best_model_name = name
            best_model_params = params

    print(f"\nSelected Model Class for final training: {best_model_name}")

    # Retrain selected best model on the FULL training set
    print(f"\nRetraining final {best_model_name} model on the FULL training set ({X_train.shape[0]} articles)...")
    start_train = time.time()
    
    if best_model_name == 'Logistic Regression':
        final_model = LogisticRegression(C=best_model_params['C'], max_iter=1000, random_state=42)
    elif best_model_name == 'Linear SVM':
        final_model = LinearSVC(C=best_model_params['C'], max_iter=2000, random_state=42, dual=False)
    else:
        final_model = RandomForestClassifier(
            n_estimators=best_model_params['n_estimators'],
            max_depth=best_model_params['max_depth'],
            random_state=42,
            n_jobs=-1
        )
        
    final_model.fit(X_train, y_train)
    print(f"Final training completed in {time.time() - start_train:.2f}s")

    # Evaluate Final Model on the FULL Test Dataset
    print("\n--- Final Model Evaluation (Full Test Set) ---")
    final_preds = final_model.predict(X_test)
    
    acc = accuracy_score(y_test, final_preds)
    prec = precision_score(y_test, final_preds)
    rec = recall_score(y_test, final_preds)
    f1 = f1_score(y_test, final_preds)
    cm = confusion_matrix(y_test, final_preds)
    
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)

    # Save artifacts
    print("\nSaving final model artifacts to model.pkl and vectorizer.pkl...")
    joblib.dump(final_model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    print("SUCCESS: New high-accuracy pipeline complete!")

if __name__ == "__main__":
    main()
