"""
Stateless Flask app for Loan Eligibility Prediction
No authentication, no database, no persistence
Only real-time ML prediction
"""
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# Load the trained model and encoders from Models directory
MODEL_DIR = 'Models'
try:
    model_path = os.path.join(MODEL_DIR, 'loan_model_real.pkl')
    encoders_path = os.path.join(MODEL_DIR, 'label_encoders_real.pkl')
    features_path = os.path.join(MODEL_DIR, 'feature_names_real.pkl')
    
    model = joblib.load(model_path)
    label_encoders = joblib.load(encoders_path)
    feature_names = joblib.load(features_path)
    
    print("✅ Model loaded successfully!")
    print(f"   Model type: {type(model).__name__}")
    print(f"   Features: {len(feature_names)}")
except Exception as e:
    print(f"⚠️  Warning: Could not load model: {e}")
    print("   Please run 'python train_new_model.py' first")
    model = None
    label_encoders = None
    feature_names = None

@app.route('/')
def home():
    """Render the dashboard"""
    return render_template('dashboard.html')

@app.route('/futuristic')
def futuristic():
    """Render the futuristic fintech dashboard"""
    return render_template('futuristic_dashboard.html')

@app.route('/futuristic-v2')
def futuristic_v2():
    """Render the new futuristic dashboard with swipe navigation"""
    return render_template('futuristic_dashboard_v2.html')

@app.route('/checker')
def checker():
    """Render the loan eligibility checker form"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests - stateless, no persistence"""
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.',
            'status': 'error'
        }), 500
    
    try:
        # Get form data
        data = request.form
        
        # Create feature dictionary in the correct order
        features = {
            'ApplicantIncome': float(data['applicant_income']),
            'CoapplicantIncome': float(data.get('coapplicant_income', 0)),
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
                except ValueError:
                    # Handle unknown category - use first class as default
                    features[col] = 0
        
        # Create feature array in correct order
        feature_array = np.array([[features[name] for name in feature_names]])
        
        # Make prediction
        prediction = model.predict(feature_array)[0]
        probability = model.predict_proba(feature_array)[0]
        
        # Calculate confidence (probability of predicted class)
        confidence = probability[1] if prediction == 1 else probability[0]
        confidence = float(confidence) * 100
        
        # Prepare response
        result = {
            'prediction': 'Approved' if prediction == 1 else 'Not Approved',
            'confidence': round(confidence, 2),
            'status': 'success'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    import os
    print("\n" + "="*60)
    print("🏦 LOAN ELIGIBILITY CHECKER")
    print("="*60)
    if model is None:
        print("\n⚠️  WARNING: Model not loaded!")
        print("Please run: python train_new_model.py")
    else:
        print("\n✅ Model loaded and ready")
    print("\nStarting Flask server...")
    print("Open your browser: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    # Only enable debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
