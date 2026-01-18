"""
Flask web application for Loan Approval Prediction
"""
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the trained model and encoders
try:
    model = joblib.load('loan_model.pkl')
    label_encoders = joblib.load('label_encoders.pkl')
    print("✓ Model and encoders loaded successfully!")
except:
    print("⚠ Model not found. Please run train_model.py first.")
    model = None
    label_encoders = None

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

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
            'ApplicantIncome': float(data['applicant_income']),
            'CoapplicantIncome': float(data['coapplicant_income']),
            'LoanAmount': float(data['loan_amount']),
            'Loan_Amount_Term': float(data['loan_term']),
            'Credit_History': float(data['credit_history']),
            'Gender': data['gender'],
            'Married': data['married'],
            'Dependents': data['dependents'],
            'Education': data['education'],
            'Self_Employed': data['self_employed'],
            'Property_Area': data['property_area']
        }
        
        # Encode categorical variables
        categorical_cols = ['Gender', 'Married', 'Dependents', 'Education', 
                           'Self_Employed', 'Property_Area']
        
        for col in categorical_cols:
            if col in label_encoders:
                try:
                    features[col] = label_encoders[col].transform([features[col]])[0]
                except:
                    features[col] = 0  # Default value if encoding fails
        
        # Create feature array in correct order
        feature_order = ['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 
                        'Loan_Amount_Term', 'Credit_History', 'Gender', 'Married', 
                        'Dependents', 'Education', 'Self_Employed', 'Property_Area']
        
        feature_array = np.array([[features[col] for col in feature_order]])
        
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
    return render_template('about.html')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("LOAN APPROVAL PREDICTION WEB APP")
    print("="*60)
    if model is None:
        print("\n⚠ WARNING: Model not loaded!")
        print("Please run the following commands first:")
        print("  1. python generate_data.py")
        print("  2. python train_model.py")
    print("\nStarting Flask server...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True)
