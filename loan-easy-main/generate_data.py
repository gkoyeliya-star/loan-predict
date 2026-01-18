"""
Generate synthetic loan application data for training
"""
import pandas as pd
import numpy as np

np.random.seed(42)

def generate_loan_data(n_samples=1000):
    """Generate synthetic loan application data"""
    
    # Generate features
    data = {
        'ApplicantIncome': np.random.randint(1000, 10000, n_samples),
        'CoapplicantIncome': np.random.randint(0, 5000, n_samples),
        'LoanAmount': np.random.randint(50, 500, n_samples),
        'Loan_Amount_Term': np.random.choice([360, 180, 120, 240, 480], n_samples),
        'Credit_History': np.random.choice([0, 1], n_samples, p=[0.15, 0.85]),
        'Gender': np.random.choice(['Male', 'Female'], n_samples),
        'Married': np.random.choice(['Yes', 'No'], n_samples, p=[0.65, 0.35]),
        'Dependents': np.random.choice(['0', '1', '2', '3+'], n_samples),
        'Education': np.random.choice(['Graduate', 'Not Graduate'], n_samples, p=[0.78, 0.22]),
        'Self_Employed': np.random.choice(['Yes', 'No'], n_samples, p=[0.15, 0.85]),
        'Property_Area': np.random.choice(['Urban', 'Semiurban', 'Rural'], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Generate target variable based on logical rules
    df['Loan_Status'] = 'N'  # Default: Not approved
    
    # Approval logic
    for idx, row in df.iterrows():
        score = 0
        
        # Income factors
        total_income = row['ApplicantIncome'] + row['CoapplicantIncome']
        if total_income > 8000:
            score += 3
        elif total_income > 5000:
            score += 2
        elif total_income > 3000:
            score += 1
            
        # Credit history (most important)
        if row['Credit_History'] == 1:
            score += 4
            
        # Education
        if row['Education'] == 'Graduate':
            score += 1
            
        # Married
        if row['Married'] == 'Yes':
            score += 1
            
        # Loan amount vs income ratio
        if total_income > 0:
            loan_income_ratio = (row['LoanAmount'] * 1000) / total_income
            if loan_income_ratio < 3:
                score += 2
            elif loan_income_ratio < 5:
                score += 1
                
        # Property area
        if row['Property_Area'] == 'Urban':
            score += 1
            
        # Self employed penalty
        if row['Self_Employed'] == 'Yes':
            score -= 1
            
        # Approval threshold
        if score >= 6:
            df.at[idx, 'Loan_Status'] = 'Y'
        elif score >= 4 and np.random.random() > 0.3:  # Some randomness
            df.at[idx, 'Loan_Status'] = 'Y'
    
    return df

if __name__ == "__main__":
    # Generate training data
    df = generate_loan_data(1000)
    df.to_csv('loan_data.csv', index=False)
    print(f"Generated {len(df)} loan applications")
    print(f"\nLoan Approval Distribution:")
    print(df['Loan_Status'].value_counts())
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nData saved to 'loan_data.csv'")
