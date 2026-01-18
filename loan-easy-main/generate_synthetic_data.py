"""
Generate realistic synthetic loan data for training
Minimum 10,000 samples with realistic distributions
"""
import pandas as pd
import numpy as np

np.random.seed(42)

def generate_synthetic_loan_data(n_samples=10000):
    """
    Generate realistic synthetic loan application data
    Features: ApplicantIncome, CoapplicantIncome, LoanAmount, Loan_Amount_Term,
              Credit_History, Gender, Married, Dependents, Education, 
              Self_Employed, Property_Area
    """
    
    print("="*70)
    print("GENERATING SYNTHETIC LOAN DATA")
    print("="*70)
    print(f"Target samples: {n_samples}")
    
    # Generate features with realistic distributions
    data = {
        # Income (realistic range: $2000 - $15000 monthly)
        'ApplicantIncome': np.random.gamma(shape=3, scale=1500, size=n_samples).astype(int) + 2000,
        
        # Co-applicant income (many have 0, others have reasonable income)
        'CoapplicantIncome': np.concatenate([
            np.zeros(int(n_samples * 0.4)),  # 40% have no co-applicant
            np.random.gamma(shape=2, scale=1000, size=int(n_samples * 0.6)).astype(int) + 1000
        ]),
        
        # Loan amount in thousands (realistic range: $50k - $500k)
        'LoanAmount': np.random.gamma(shape=4, scale=30, size=n_samples).astype(int) + 50,
        
        # Loan term (most common: 360 months = 30 years)
        'Loan_Amount_Term': np.random.choice([360, 180, 240, 120, 480], 
                                             n_samples, 
                                             p=[0.70, 0.15, 0.10, 0.03, 0.02]),
        
        # Credit history (85% have good credit)
        'Credit_History': np.random.choice([0, 1], n_samples, p=[0.15, 0.85]),
        
        # Gender (realistic distribution)
        'Gender': np.random.choice(['Male', 'Female'], n_samples, p=[0.60, 0.40]),
        
        # Marital status (65% married)
        'Married': np.random.choice(['Yes', 'No'], n_samples, p=[0.65, 0.35]),
        
        # Number of dependents
        'Dependents': np.random.choice(['0', '1', '2', '3+'], 
                                       n_samples, 
                                       p=[0.50, 0.25, 0.20, 0.05]),
        
        # Education (78% graduates)
        'Education': np.random.choice(['Graduate', 'Not Graduate'], 
                                      n_samples, 
                                      p=[0.78, 0.22]),
        
        # Self-employed (15% self-employed)
        'Self_Employed': np.random.choice(['No', 'Yes'], n_samples, p=[0.85, 0.15]),
        
        # Property area
        'Property_Area': np.random.choice(['Urban', 'Semiurban', 'Rural'], 
                                          n_samples, 
                                          p=[0.40, 0.35, 0.25])
    }
    
    # Shuffle co-applicant income
    np.random.shuffle(data['CoapplicantIncome'])
    
    df = pd.DataFrame(data)
    
    # Generate target variable based on explainable rules
    # Credit history is the strongest factor, followed by income-to-loan ratio
    df['Loan_Status'] = 'N'  # Default: Not approved
    
    print("\nApplying approval logic...")
    
    for idx, row in df.iterrows():
        score = 0
        
        # CREDIT HISTORY - Strongest factor (worth 5 points)
        if row['Credit_History'] == 1:
            score += 5
        else:
            score -= 3  # Poor credit is a major red flag
        
        # INCOME-TO-LOAN RATIO - Second most important
        total_income = row['ApplicantIncome'] + row['CoapplicantIncome']
        loan_amount_dollars = row['LoanAmount'] * 1000
        
        if total_income > 0:
            # Monthly payment estimation (rough)
            loan_to_income_ratio = loan_amount_dollars / (total_income * 12)
            
            if loan_to_income_ratio < 2:  # Very affordable
                score += 4
            elif loan_to_income_ratio < 3:  # Affordable
                score += 3
            elif loan_to_income_ratio < 4:  # Manageable
                score += 2
            elif loan_to_income_ratio < 5:  # Stretching
                score += 1
            else:  # Too high
                score -= 1
        
        # HOUSEHOLD INCOME - Total income matters
        if total_income > 10000:
            score += 2
        elif total_income > 7000:
            score += 1
        elif total_income < 3000:
            score -= 1
        
        # EDUCATION - Slight positive factor
        if row['Education'] == 'Graduate':
            score += 1
        
        # MARRIED - Stability factor
        if row['Married'] == 'Yes':
            score += 1
        
        # PROPERTY AREA - Urban properties may have better prospects
        if row['Property_Area'] == 'Urban':
            score += 1
        elif row['Property_Area'] == 'Rural':
            score -= 0.5
        
        # SELF EMPLOYED - Slight risk factor
        if row['Self_Employed'] == 'Yes':
            score -= 0.5
        
        # DEPENDENTS - More dependents = more financial burden
        if row['Dependents'] == '3+':
            score -= 1
        elif row['Dependents'] in ['1', '2']:
            score -= 0.5
        
        # LOAN TERM - Longer terms are easier to approve
        if row['Loan_Amount_Term'] >= 360:
            score += 0.5
        
        # FINAL APPROVAL DECISION
        # High score = definitely approved
        if score >= 8:
            df.at[idx, 'Loan_Status'] = 'Y'
        # Good score = likely approved
        elif score >= 6:
            if np.random.random() > 0.15:  # 85% approval
                df.at[idx, 'Loan_Status'] = 'Y'
        # Medium score = 50/50 chance
        elif score >= 4:
            if np.random.random() > 0.5:
                df.at[idx, 'Loan_Status'] = 'Y'
        # Low score = small chance
        elif score >= 2:
            if np.random.random() > 0.85:  # 15% approval
                df.at[idx, 'Loan_Status'] = 'Y'
        # Very low score = rejection
        else:
            df.at[idx, 'Loan_Status'] = 'N'
    
    return df

if __name__ == "__main__":
    # Generate training data
    df = generate_synthetic_loan_data(10000)
    
    # Save to CSV
    output_file = 'synthetic_loan_data.csv'
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("DATA GENERATION COMPLETE")
    print("="*70)
    print(f"\nTotal samples: {len(df)}")
    print(f"\nLoan Status Distribution:")
    status_counts = df['Loan_Status'].value_counts()
    print(f"  Approved (Y): {status_counts.get('Y', 0)} ({status_counts.get('Y', 0)/len(df)*100:.1f}%)")
    print(f"  Rejected (N): {status_counts.get('N', 0)} ({status_counts.get('N', 0)/len(df)*100:.1f}%)")
    
    print(f"\nFeature Statistics:")
    print(df.describe())
    
    print(f"\nCategorical Features:")
    for col in ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'Property_Area']:
        print(f"\n{col}:")
        print(df[col].value_counts())
    
    print(f"\n✅ Data saved to '{output_file}'")
    print(f"\nNext step: Run 'python train_new_model.py' to train the model!")
