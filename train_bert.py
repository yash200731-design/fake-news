import os
import re
import time
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback

def clean_text_bert(text):
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class NewsDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    
    # Softmax to get probabilities for AUC
    exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
    probs_fake = probs[:, 1]
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    try:
        auc = roc_auc_score(labels, probs_fake)
    except Exception:
        auc = 0.5
        
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'roc_auc': auc
    }

def main():
    print("Loading datasets...")
    true_df = pd.read_csv('true.csv')
    fake_df = pd.read_csv('fake.csv')

    true_df['label'] = 0  # Real
    fake_df['label'] = 1  # Fake

    df = pd.concat([true_df, fake_df], ignore_index=True)
    
    # Preprocessing
    print("Combining title and text...")
    df['combined'] = df['title'] + " " + df['text']
    
    print("Cleaning text...")
    df['cleaned'] = df['combined'].apply(clean_text_bert)
    
    # Remove empty records
    df = df[df['cleaned'].str.strip() != '']
    df = df.dropna(subset=['cleaned'])
    
    # Remove duplicate articles
    print(f"Dataset size before deduplication: {len(df)}")
    df.drop_duplicates(subset=['cleaned'], keep='first', inplace=True)
    print(f"Dataset size after deduplication: {len(df)}")

    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Check GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # If running on CPU, downsample to ensure it completes quickly
    if device == "cpu":
        print("CPU mode: Downsampling dataset to 2,000 balanced samples to speed up training...")
        fake_subset = df[df['label'] == 1].sample(1000, random_state=42)
        real_subset = df[df['label'] == 0].sample(1000, random_state=42)
        df_balanced = pd.concat([fake_subset, real_subset], ignore_index=True)
        df_final = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    else:
        print("GPU mode: Utilizing 8,000 balanced samples for optimal VRAM training...")
        fake_subset = df[df['label'] == 1].sample(min(4000, len(df[df['label'] == 1])), random_state=42)
        real_subset = df[df['label'] == 0].sample(min(4000, len(df[df['label'] == 0])), random_state=42)
        df_balanced = pd.concat([fake_subset, real_subset], ignore_index=True)
        df_final = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

    # 80/10/10 train-validation-test split
    train_df, temp_df = train_test_split(df_final, test_size=0.2, random_state=42, stratify=df_final['label'])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label'])
    
    print(f"Split sizes: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    # Load Tokenizer
    print("Loading DistilBERT tokenizer...")
    tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

    # Tokenize
    print("Tokenizing datasets...")
    train_encodings = tokenizer(list(train_df['cleaned']), truncation=True, padding=True, max_length=256)
    val_encodings = tokenizer(list(val_df['cleaned']), truncation=True, padding=True, max_length=256)
    test_encodings = tokenizer(list(test_df['cleaned']), truncation=True, padding=True, max_length=256)

    # Prepare datasets
    train_dataset = NewsDataset(train_encodings, list(train_df['label']))
    val_dataset = NewsDataset(val_encodings, list(val_df['label']))
    test_dataset = NewsDataset(test_encodings, list(test_df['label']))

    # Load Model
    print("Loading DistilBERT model...")
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
    model.to(device)

    # Training Arguments
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        eval_strategy='steps',
        eval_steps=20,
        save_steps=20,
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model='f1',
        greater_is_better=True,
        report_to='none'
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    print("Starting DistilBERT fine-tuning...")
    trainer.train()

    # Save model and tokenizer
    print("Saving the best model and tokenizer...")
    model_path = "./best_model"
    trainer.save_model(model_path)
    tokenizer.save_pretrained(model_path)
    print(f"Model saved to {model_path}")

    # Final Evaluation on Test Set
    print("\nEvaluating on Test Set...")
    predictions_output = trainer.predict(test_dataset)
    logits = predictions_output.predictions
    labels = predictions_output.label_ids
    
    preds = np.argmax(logits, axis=1)
    exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
    probs_fake = probs[:, 1]
    
    accuracy = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    roc_auc = roc_auc_score(labels, probs_fake)
    cm = confusion_matrix(labels, preds)

    print("\n--- FINAL TEST EVALUATION METRICS ---")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("--------------------------------------")

if __name__ == "__main__":
    main()
