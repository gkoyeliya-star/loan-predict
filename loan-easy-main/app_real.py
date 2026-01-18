"""
Flask web application for Loan Approval Prediction - REAL DATASET
"""
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the trained model and encoders
try:
    model = joblib.load('loan_model_real.pkl')
    label_encoders = joblib.load('label_encoders_real.pkl')
    feature_names = joblib.load('feature_names_real.pkl')
    print("✓ Real dataset model and encoders loaded successfully!")
    print(f"✓ Model type: {type(model).__name__}")
    print(f"✓ Features: {feature_names}")
except:
    print("⚠ Model not found. Please run train_model_real.py first.")
    model = None
    label_encoders = None
    feature_names = None

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index_real.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.'
        }), 500
    
    try:
        # Get form data
        data = request.form
        
        # Create feature dictionary
        features = {
            'no_of_dependents': int(data['no_of_dependents']),
            'education': data['education'],
            'self_employed': data['self_employed'],
            'income_annum': float(data['income_annum']),
            'loan_amount': float(data['loan_amount']),
            'loan_term': int(data['loan_term']),
            'cibil_score': int(data['cibil_score']),
            'residential_assets_value': float(data['residential_assets_value']),
            'commercial_assets_value': float(data['commercial_assets_value']),
            'luxury_assets_value': float(data['luxury_assets_value']),
            'bank_asset_value': float(data['bank_asset_value'])
        }
        
        # Encode categorical variables
        for col in ['education', 'self_employed']:
            if col in label_encoders:
                try:
                    features[col] = label_encoders[col].transform([features[col]])[0]
                except:
                    features[col] = 0  # Default value if encoding fails
        
        # Create feature array in correct order
        feature_array = np.array([[features[col] for col in feature_names]])
        
        # Make prediction
        prediction = model.predict(feature_array)[0]
        probability = model.predict_proba(feature_array)[0]
        
        # Prepare response
        result = {
            'prediction': 'Approved' if prediction == 1 else 'Not Approved',
            'probability': float(probability[1]) * 100,  # Probability of approval
            'status': 'success'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about_real.html')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("LOAN APPROVAL PREDICTION WEB APP - REAL DATASET")
    print("="*60)
    if model is None:
        print("\n⚠ WARNING: Model not loaded!")
        print("Please run the following command first:")
        print("  python train_model_real.py")
    else:
        print(f"\n✓ Model: Gradient Boosting (98.5% accuracy)")
        print(f"✓ Trained on: 4,269 real applications")
        print(f"✓ Most important feature: CIBIL Score (82%)")
    print("\nStarting Flask server...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
