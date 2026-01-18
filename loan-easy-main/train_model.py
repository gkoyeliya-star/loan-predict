"""
Train and evaluate loan approval prediction models
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_preprocess_data(filepath='loan_data.csv'):
    """Load and preprocess the loan data"""
    df = pd.read_csv(filepath)
    
    print("Original Data Shape:", df.shape)
    print("\nMissing Values:")
    print(df.isnull().sum())
    
    # Handle missing values (if any)
    df = df.dropna()
    
    # Encode categorical variables
    label_encoders = {}
    categorical_cols = ['Gender', 'Married', 'Dependents', 'Education', 
                       'Self_Employed', 'Property_Area']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Save label encoders
    joblib.dump(label_encoders, 'label_encoders.pkl')
    
    # Prepare features and target
    X = df.drop('Loan_Status', axis=1)
    y = df['Loan_Status'].map({'Y': 1, 'N': 0})
    
    return X, y, df

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple classification models"""
    
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=5),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', random_state=42, probability=True)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"Training {name}...")
        print('='*50)
        
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
        print(classification_report(y_test, y_pred, target_names=['Not Approved', 'Approved']))
        
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

def plot_results(results, y_test):
    """Plot model comparison and confusion matrices"""
    
    # Model Comparison
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
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
    ax1.set_xticklabels(model_names, rotation=45)
    ax1.legend()
    ax1.set_ylim([0, 1])
    
    # Confusion Matrices
    for idx, (name, result) in enumerate(results.items()):
        if idx < 3:
            row = (idx + 1) // 2
            col = (idx + 1) % 2
            ax = axes[row, col]
            
            sns.heatmap(result['confusion_matrix'], annot=True, fmt='d', 
                       cmap='Blues', ax=ax, cbar=False)
            ax.set_title(f'{name} - Confusion Matrix')
            ax.set_ylabel('Actual')
            ax.set_xlabel('Predicted')
            ax.set_xticklabels(['Not Approved', 'Approved'])
            ax.set_yticklabels(['Not Approved', 'Approved'])
    
    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✓ Model comparison plot saved as 'model_comparison.png'")
    plt.close()

def save_best_model(results):
    """Save the best performing model"""
    best_model_name = max(results, key=lambda x: results[x]['accuracy'])
    best_model = results[best_model_name]['model']
    
    joblib.dump(best_model, 'loan_model.pkl')
    
    with open('model_info.txt', 'w') as f:
        f.write(f"Best Model: {best_model_name}\n")
        f.write(f"Accuracy: {results[best_model_name]['accuracy']:.4f}\n")
        f.write(f"CV Score: {results[best_model_name]['cv_score']:.4f}\n")
    
    print(f"\n✓ Best model ({best_model_name}) saved as 'loan_model.pkl'")
    print(f"✓ Accuracy: {results[best_model_name]['accuracy']:.4f}")
    
    return best_model_name

if __name__ == "__main__":
    print("="*60)
    print("LOAN APPROVAL PREDICTION MODEL TRAINING")
    print("="*60)
    
    # Load and preprocess data
    X, y, df = load_and_preprocess_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining Set: {X_train.shape[0]} samples")
    print(f"Test Set: {X_test.shape[0]} samples")
    
    # Train models
    results = train_models(X_train, X_test, y_train, y_test)
    
    # Plot results
    plot_results(results, y_test)
    
    # Save best model
    best_model_name = save_best_model(results)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("="*60)
