"""
Train loan approval model on synthetic data
Requirements:
- Python 3.11
- scikit-learn==1.3.2
- numpy==1.26.4
- No lambdas, no closures, no sklearn internal APIs
- Use GradientBoostingClassifier or RandomForestClassifier
- Set random_state for reproducibility
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

def load_and_preprocess_data(filepath='synthetic_loan_data.csv'):
    """Load and preprocess the synthetic loan dataset"""
    print("="*70)
    print("LOADING SYNTHETIC LOAN DATASET")
    print("="*70)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}\nPlease run 'python generate_synthetic_data.py' first!")
    
    df = pd.read_csv(filepath)
    
    print(f"\nOriginal Data Shape: {df.shape}")
    print(f"Total Applications: {len(df)}")
    
    # Check for missing values
    print("\nMissing Values:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("  ✓ No missing values")
    else:
        print(missing[missing > 0])
    
    # Check target distribution
    print("\nLoan Status Distribution:")
    print(df['Loan_Status'].value_counts())
    approval_rate = (df['Loan_Status']=='Y').sum()/len(df)*100
    print(f"Approval Rate: {approval_rate:.1f}%")
    
    # Encode categorical variables
    print("\nEncoding categorical variables...")
    label_encoders = {}
    
    categorical_cols = ['Gender', 'Married', 'Dependents', 'Education', 
                       'Self_Employed', 'Property_Area']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        print(f"  ✓ Encoded '{col}': {dict(zip(le.classes_, le.transform(le.classes_)))}")
    
    # Prepare features and target
    X = df.drop('Loan_Status', axis=1)
    y = df['Loan_Status'].map({'Y': 1, 'N': 0})
    
    print(f"\n✓ Feature Matrix X: {X.shape}")
    print(f"✓ Target Vector y: {y.shape}")
    
    # Feature names
    feature_names = X.columns.tolist()
    print(f"\nFeatures: {feature_names}")
    
    return X, y, label_encoders, feature_names

def train_models(X_train, X_test, y_train, y_test, feature_names):
    """Train classification models"""
    
    print("\n" + "="*70)
    print("TRAINING MODELS")
    print("="*70)
    
    # Define models with reproducible random_state
    models = {
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        ),
        'RandomForest': RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n{'='*70}")
        print(f"Training {name}...")
        print('='*70)
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Evaluation
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation score (5-fold)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        
        print(f"\n✓ Accuracy: {accuracy:.4f}")
        print(f"✓ Cross-Validation Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Rejected', 'Approved']))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(cm)
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            print(f"\nTop 5 Most Important Features:")
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:5]
            for i, idx in enumerate(indices, 1):
                print(f"  {i}. {feature_names[idx]}: {importances[idx]:.4f}")
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'cv_score': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'predictions': y_pred,
            'confusion_matrix': cm
        }
    
    return results

def save_best_model(results, label_encoders, feature_names, output_dir='Models'):
    """Save the best performing model and associated files"""
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\n✓ Created directory: {output_dir}")
    
    # Find best model
    best_model_name = max(results, key=lambda x: results[x]['accuracy'])
    best_model = results[best_model_name]['model']
    best_accuracy = results[best_model_name]['accuracy']
    best_cv_score = results[best_model_name]['cv_score']
    
    # Save model
    model_path = os.path.join(output_dir, 'loan_model_real.pkl')
    joblib.dump(best_model, model_path)
    print(f"\n✓ Best model ({best_model_name}) saved to: {model_path}")
    
    # Save label encoders
    encoders_path = os.path.join(output_dir, 'label_encoders_real.pkl')
    joblib.dump(label_encoders, encoders_path)
    print(f"✓ Label encoders saved to: {encoders_path}")
    
    # Save feature names
    features_path = os.path.join(output_dir, 'feature_names_real.pkl')
    joblib.dump(feature_names, features_path)
    print(f"✓ Feature names saved to: {features_path}")
    
    # Save model info
    info_path = os.path.join(output_dir, 'model_info_real.txt')
    with open(info_path, 'w') as f:
        f.write(f"Best Model: {best_model_name}\n")
        f.write(f"Accuracy: {best_accuracy:.4f}\n")
        f.write(f"CV Score: {best_cv_score:.4f}\n")
        f.write(f"\nFeatures used:\n")
        for feat in feature_names:
            f.write(f"  - {feat}\n")
        
        # Feature importance
        if hasattr(best_model, 'feature_importances_'):
            f.write(f"\nFeature Importance:\n")
            importances = best_model.feature_importances_
            indices = np.argsort(importances)[::-1]
            for idx in indices:
                f.write(f"  {feature_names[idx]}: {importances[idx]:.4f}\n")
    
    print(f"✓ Model info saved to: {info_path}")
    
    # Display summary
    print("\n" + "="*70)
    print("MODEL TRAINING COMPLETE")
    print("="*70)
    print(f"\n✅ Best Model: {best_model_name}")
    print(f"✅ Accuracy: {best_accuracy:.4f}")
    print(f"✅ CV Score: {best_cv_score:.4f}")
    print(f"\n✅ All artifacts saved to '{output_dir}/' directory")
    
    return best_model_name

if __name__ == "__main__":
    print("\n" + "="*70)
    print("LOAN APPROVAL MODEL TRAINING")
    print("Python 3.11 | scikit-learn 1.3.2")
    print("="*70)
    
    try:
        # Load and preprocess data
        X, y, label_encoders, feature_names = load_and_preprocess_data()
        
        # Split data (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n{'='*70}")
        print("DATA SPLIT")
        print('='*70)
        print(f"Training Set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
        print(f"Test Set: {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")
        
        # Train models
        results = train_models(X_train, X_test, y_train, y_test, feature_names)
        
        # Save best model
        best_model_name = save_best_model(results, label_encoders, feature_names)
        
        print("\n✅ SUCCESS! Model is ready for deployment.")
        print("\nNext steps:")
        print("  1. Update app.py to load the model from Models/ directory")
        print("  2. Test the prediction flow")
        print("  3. Deploy to Render")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise
