"""
Train loan approval model on REAL dataset
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_preprocess_real_data(filepath='real_data/loan_approval_dataset.csv'):
    """Load and preprocess the real loan dataset"""
    df = pd.read_csv(filepath)
    
    print("="*70)
    print("REAL LOAN DATASET ANALYSIS")
    print("="*70)
    print(f"\nOriginal Data Shape: {df.shape}")
    print(f"Total Applications: {len(df)}")
    
    # Clean column names (remove leading spaces)
    df.columns = df.columns.str.strip()
    
    print("\nColumns:", df.columns.tolist())
    
    # Check target distribution
    print("\nLoan Status Distribution:")
    print(df['loan_status'].value_counts())
    print(f"Approval Rate: {(df['loan_status']=='Approved').sum()/len(df)*100:.1f}%")
    
    # Handle missing values
    print("\nMissing Values:")
    print(df.isnull().sum())
    
    # Drop loan_id as it's not a feature
    if 'loan_id' in df.columns:
        df = df.drop('loan_id', axis=1)
        print("\n✓ Dropped 'loan_id' column")
    
    # Encode categorical variables
    print("\nEncoding categorical variables...")
    label_encoders = {}
    categorical_cols = ['education', 'self_employed']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        print(f"  ✓ Encoded '{col}': {dict(zip(le.classes_, le.transform(le.classes_)))}")
    
    # Save label encoders
    joblib.dump(label_encoders, 'label_encoders_real.pkl')
    
    # Prepare features and target
    X = df.drop('loan_status', axis=1)
    # Strip spaces from loan_status values
    df['loan_status'] = df['loan_status'].str.strip()
    y = df['loan_status'].map({'Approved': 1, 'Rejected': 0})
    
    print(f"\n✓ Feature Matrix X: {X.shape}")
    print(f"✓ Target Vector y: {y.shape}")
    
    # Feature statistics
    print("\n" + "="*70)
    print("FEATURE STATISTICS")
    print("="*70)
    print(X.describe())
    
    return X, y, df, label_encoders

def analyze_feature_correlations(df):
    """Analyze feature correlations with target"""
    print("\n" + "="*70)
    print("FEATURE ANALYSIS")
    print("="*70)
    
    # CIBIL Score impact
    print("\nCIBIL Score vs Approval:")
    df['cibil_category'] = pd.cut(df['cibil_score'], 
                                   bins=[0, 550, 650, 750, 900],
                                   labels=['Poor (<550)', 'Fair (550-650)', 'Good (650-750)', 'Excellent (>750)'])
    cibil_impact = df.groupby('cibil_category')['loan_status'].apply(
        lambda x: (x=='Approved').sum()/len(x)*100
    )
    print(cibil_impact)
    
    # Income impact
    print("\nIncome Level vs Approval:")
    df['income_category'] = pd.cut(df['income_annum'], 
                                   bins=[0, 2000000, 5000000, 10000000, 100000000],
                                   labels=['Low (<2M)', 'Medium (2-5M)', 'High (5-10M)', 'Very High (>10M)'])
    income_impact = df.groupby('income_category')['loan_status'].apply(
        lambda x: (x=='Approved').sum()/len(x)*100
    )
    print(income_impact)
    
    # Loan amount impact
    print("\nLoan Amount vs Approval:")
    df['loan_category'] = pd.cut(df['loan_amount'], 
                                 bins=[0, 5000000, 10000000, 20000000, 100000000],
                                 labels=['Small (<5M)', 'Medium (5-10M)', 'Large (10-20M)', 'Very Large (>20M)'])
    loan_impact = df.groupby('loan_category')['loan_status'].apply(
        lambda x: (x=='Approved').sum()/len(x)*100
    )
    print(loan_impact)

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple classification models"""
    
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=10),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5),
        'SVM': SVC(kernel='rbf', random_state=42, probability=True)
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
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        
        print(f"\nAccuracy: {accuracy:.4f}")
        print(f"Cross-Validation Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Rejected', 'Approved']))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'cv_score': cv_scores.mean(),
            'predictions': y_pred,
            'confusion_matrix': cm
        }
    
    return results

def plot_results(results, y_test, X):
    """Plot model comparison and feature importance"""
    
    # Model Comparison
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Accuracy Comparison
    model_names = list(results.keys())
    accuracies = [results[name]['accuracy'] for name in model_names]
    cv_scores = [results[name]['cv_score'] for name in model_names]
    
    ax1 = axes[0, 0]
    x_pos = np.arange(len(model_names))
    ax1.bar(x_pos - 0.2, accuracies, 0.4, label='Test Accuracy', color='skyblue')
    ax1.bar(x_pos + 0.2, cv_scores, 0.4, label='CV Score', color='lightcoral')
    ax1.set_xlabel('Models')
    ax1.set_ylabel('Score')
    ax1.set_title('Model Performance Comparison')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(model_names, rotation=45, ha='right')
    ax1.legend()
    ax1.set_ylim([0, 1])
    ax1.grid(axis='y', alpha=0.3)
    
    # Confusion Matrices (first 4 models)
    for idx, (name, result) in enumerate(list(results.items())[:4]):
        if idx < 4:
            row = (idx + 1) // 3
            col = (idx + 1) % 3
            ax = axes[row, col]
            
            sns.heatmap(result['confusion_matrix'], annot=True, fmt='d', 
                       cmap='Blues', ax=ax, cbar=False)
            ax.set_title(f'{name}\nAccuracy: {result["accuracy"]:.3f}')
            ax.set_ylabel('Actual')
            ax.set_xlabel('Predicted')
            ax.set_xticklabels(['Rejected', 'Approved'])
            ax.set_yticklabels(['Rejected', 'Approved'])
    
    # Feature importance for best model
    best_model_name = max(results, key=lambda x: results[x]['accuracy'])
    best_model = results[best_model_name]['model']
    
    ax_feat = axes[1, 2]
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        feature_names = X.columns
        
        # Sort by importance
        indices = np.argsort(importances)[::-1][:10]  # Top 10
        
        ax_feat.barh(range(len(indices)), importances[indices], color='green', alpha=0.7)
        ax_feat.set_yticks(range(len(indices)))
        ax_feat.set_yticklabels([feature_names[i] for i in indices])
        ax_feat.set_xlabel('Importance')
        ax_feat.set_title(f'Top 10 Features ({best_model_name})')
        ax_feat.invert_yaxis()
    else:
        ax_feat.text(0.5, 0.5, 'Feature importance not available\nfor this model', 
                    ha='center', va='center')
        ax_feat.set_title(f'{best_model_name}')
    
    plt.tight_layout()
    plt.savefig('real_model_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✓ Model comparison plot saved as 'real_model_comparison.png'")
    plt.close()

def save_best_model(results, X):
    """Save the best performing model"""
    best_model_name = max(results, key=lambda x: results[x]['accuracy'])
    best_model = results[best_model_name]['model']
    
    joblib.dump(best_model, 'loan_model_real.pkl')
    
    # Save feature names
    joblib.dump(X.columns.tolist(), 'feature_names_real.pkl')
    
    with open('model_info_real.txt', 'w') as f:
        f.write(f"Best Model: {best_model_name}\n")
        f.write(f"Accuracy: {results[best_model_name]['accuracy']:.4f}\n")
        f.write(f"CV Score: {results[best_model_name]['cv_score']:.4f}\n")
        f.write(f"\nFeatures used:\n")
        for feat in X.columns:
            f.write(f"  - {feat}\n")
    
    print(f"\n✓ Best model ({best_model_name}) saved as 'loan_model_real.pkl'")
    print(f"✓ Accuracy: {results[best_model_name]['accuracy']:.4f}")
    print(f"✓ CV Score: {results[best_model_name]['cv_score']:.4f}")
    
    # Feature importance
    if hasattr(best_model, 'feature_importances_'):
        print("\n" + "="*70)
        print("FEATURE IMPORTANCE (Most to Least Important)")
        print("="*70)
        importances = best_model.feature_importances_
        feature_importance = pd.DataFrame({
            'Feature': X.columns,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        for idx, row in feature_importance.iterrows():
            bars = '█' * int(row['Importance'] * 100)
            print(f"  {row['Feature']:30s} {row['Importance']:.4f} {bars}")
    
    return best_model_name

if __name__ == "__main__":
    print("\n" + "="*70)
    print("LOAN APPROVAL MODEL TRAINING - REAL DATASET")
    print("="*70)
    
    # Load and preprocess data
    X, y, df, label_encoders = load_and_preprocess_real_data()
    
    # Analyze features
    analyze_feature_correlations(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n{'='*70}")
    print("DATA SPLIT")
    print('='*70)
    print(f"Training Set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
    print(f"Test Set: {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")
    
    # Train models
    results = train_models(X_train, X_test, y_train, y_test)
    
    # Plot results
    plot_results(results, y_test, X)
    
    # Save best model
    best_model_name = save_best_model(results, X)
    
    print("\n" + "="*70)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"\n✅ Best Model: {best_model_name}")
    print(f"✅ Trained on {len(X)} real loan applications")
    print(f"✅ Model saved as: loan_model_real.pkl")
    print(f"✅ Encoders saved as: label_encoders_real.pkl")
    print(f"✅ Feature names saved as: feature_names_real.pkl")
    print(f"\nNext step: Update app.py to use the new model!")
