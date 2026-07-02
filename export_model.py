import joblib
import json
import math
import re

def export():
    # Load scikit-learn models
    model = joblib.load('model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')

    # Extract coefficients, intercept, vocabulary mapping, and idfs
    # Convert numpy types to standard python types for JSON serialization
    vocabulary = {str(k): int(v) for k, v in vectorizer.vocabulary_.items()}
    idf = [float(x) for x in vectorizer.idf_]
    coef = [float(x) for x in model.coef_[0]]
    intercept = float(model.intercept_[0])

    model_data = {
        'vocabulary': vocabulary,
        'idf': idf,
        'coef': coef,
        'intercept': intercept
    }

    # Save to JSON
    with open('model_data.json', 'w') as f:
        json.dump(model_data, f)
    print("SUCCESS: Model parameters exported to model_data.json!")

if __name__ == "__main__":
    export()
