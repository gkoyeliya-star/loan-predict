"""
Verification Module for Loan Easy
Simulates verification of financial documents and information
In production, these would connect to actual government/banking APIs
"""

import re
import random
from datetime import datetime

class VerificationService:
    """Service to verify user documents and information"""
    
    # Simulated database of valid PAN cards (in production, this would be API call to Income Tax Dept)
    VALID_PAN_DATABASE = {
        'ABCDE1234F': {'name': 'JOHN DOE', 'dob': '1990-01-15', 'status': 'Active'},
        'ABCDE5678G': {'name': 'JANE SMITH', 'dob': '1985-06-20', 'status': 'Active'},
        'DEFGH9012H': {'name': 'RAM KUMAR', 'dob': '1992-03-10', 'status': 'Active'},
        'PQRST3456J': {'name': 'DEBJIT DEB BARMAN', 'dob': '1995-07-25', 'status': 'Active'},
    }
    
    # Simulated valid IFSC codes (first 4 characters = bank code)
    VALID_BANKS = {
        'SBIN': 'State Bank of India',
        'HDFC': 'HDFC Bank',
        'ICIC': 'ICICI Bank',
        'AXIS': 'Axis Bank',
        'PUNB': 'Punjab National Bank',
        'BARB': 'Bank of Baroda',
        'UBIN': 'Union Bank of India',
        'CNRB': 'Canara Bank',
        'IDIB': 'IDBI Bank',
        'KKBK': 'Kotak Mahindra Bank',
    }
    
    @staticmethod
    def verify_pan_card(pan_number, user_name, dob):
        """
        Verify PAN card with Income Tax Department
        Returns: (is_valid, message, details)
        """
        # Format validation
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_pattern, pan_number.upper()):
            return False, "Invalid PAN format. Format should be: ABCDE1234F", None
        
        pan_upper = pan_number.upper()
        
        # Simulated verification with database
        if pan_upper in VerificationService.VALID_PAN_DATABASE:
            pan_data = VerificationService.VALID_PAN_DATABASE[pan_upper]
            return True, f"PAN verified successfully with Income Tax Department", {
                'registered_name': pan_data['name'],
                'status': pan_data['status'],
                'verified_at': datetime.now().isoformat()
            }
        
        # For demo purposes, accept any valid format and simulate verification
        # In production, this would query actual government database
        return True, f"PAN {pan_upper} verified (Simulated)", {
            'registered_name': user_name.upper(),
            'status': 'Active',
            'verified_at': datetime.now().isoformat(),
            'note': 'Simulated verification - In production, this connects to Income Tax API'
        }
    
    @staticmethod
    def verify_aadhar(aadhar_number, user_name, dob):
        """
        Verify Aadhar with UIDAI
        Returns: (is_valid, message, details)
        """
        # Remove spaces and validate format
        aadhar_clean = aadhar_number.replace(' ', '').replace('-', '')
        
        if len(aadhar_clean) != 12 or not aadhar_clean.isdigit():
            return False, "Invalid Aadhar format. Must be 12 digits", None
        
        # Simulated Verhoeff algorithm check (simplified)
        # In production, this would use actual Verhoeff algorithm
        
        # Simulate UIDAI API call
        # In production: Connect to UIDAI e-KYC API
        verification_result = {
            'verified': True,
            'name_match': 'Exact Match',
            'address_available': True,
            'verified_at': datetime.now().isoformat(),
            'note': 'Simulated verification - In production, this connects to UIDAI API'
        }
        
        return True, f"Aadhar verified with UIDAI", verification_result
    
    @staticmethod
    def verify_bank_account(account_number, ifsc_code, account_holder_name, bank_name):
        """
        Verify bank account with NPCI/Bank
        Returns: (is_valid, message, details)
        """
        # IFSC format validation
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        ifsc_upper = ifsc_code.upper()
        
        if not re.match(ifsc_pattern, ifsc_upper):
            return False, "Invalid IFSC Code format. Format: SBIN0001234", None
        
        # Extract bank code (first 4 characters)
        bank_code = ifsc_upper[:4]
        
        # Verify bank code exists
        if bank_code not in VerificationService.VALID_BANKS:
            return False, f"Bank code {bank_code} not recognized. Please check IFSC code.", None
        
        verified_bank_name = VerificationService.VALID_BANKS[bank_code]
        
        # Account number validation (basic)
        account_clean = account_number.replace(' ', '').replace('-', '')
        if len(account_clean) < 9 or len(account_clean) > 18:
            return False, "Invalid account number length. Must be 9-18 digits", None
        
        # Simulated bank account verification via NPCI
        # In production: Use Penny Drop API or Bank Account Verification API
        verification_result = {
            'verified': True,
            'bank_name': verified_bank_name,
            'account_active': True,
            'account_holder_name': account_holder_name,
            'name_match_score': random.randint(85, 100),
            'ifsc_valid': True,
            'branch_city': 'Mumbai',  # Would come from IFSC lookup
            'verified_at': datetime.now().isoformat(),
            'verification_method': 'NPCI Penny Drop (Simulated)',
            'note': 'Simulated verification - In production, this uses Penny Drop API'
        }
        
        return True, f"Bank account verified with {verified_bank_name}", verification_result
    
    @staticmethod
    def verify_cibil_score(pan_number, reported_score):
        """
        Verify CIBIL score with credit bureau
        Returns: (is_valid, actual_score, message, details)
        """
        # Simulate CIBIL API call
        # In production: Connect to TransUnion CIBIL API or Equifax/Experian
        
        # For simulation, we'll accept the reported score with some variance
        actual_score = reported_score + random.randint(-20, 20)
        actual_score = max(300, min(900, actual_score))  # Keep in valid range
        
        score_variance = abs(actual_score - reported_score)
        
        if score_variance <= 10:
            status = "Verified - Score matches"
        elif score_variance <= 30:
            status = "Verified - Minor variance detected"
        else:
            status = "Discrepancy - Please update score"
        
        verification_result = {
            'reported_score': reported_score,
            'actual_score': actual_score,
            'variance': score_variance,
            'status': status,
            'credit_accounts': random.randint(1, 8),
            'active_loans': random.randint(0, 3),
            'credit_history_months': random.randint(12, 120),
            'last_updated': datetime.now().isoformat(),
            'bureau': 'TransUnion CIBIL (Simulated)',
            'note': 'Simulated verification - In production, this connects to CIBIL API'
        }
        
        is_valid = score_variance <= 50
        message = f"CIBIL Score: {actual_score} (Reported: {reported_score})"
        
        return is_valid, actual_score, message, verification_result
    
    @staticmethod
    def verify_income(pan_number, reported_income, employment_type):
        """
        Verify income with Income Tax records
        Returns: (is_valid, message, details)
        """
        # Simulate ITR verification
        # In production: Connect to Income Tax Department API for ITR data
        
        # Generate simulated ITR data
        itr_income = reported_income * random.uniform(0.8, 1.2)
        variance_percent = abs((itr_income - reported_income) / reported_income * 100)
        
        verification_result = {
            'reported_income': reported_income,
            'itr_income': round(itr_income, 2),
            'variance_percent': round(variance_percent, 2),
            'last_itr_filed': '2024-2025',
            'itr_status': 'Filed & Verified',
            'employment_type': employment_type,
            'verified_at': datetime.now().isoformat(),
            'note': 'Simulated verification - In production, this connects to Income Tax API'
        }
        
        is_valid = variance_percent <= 30
        
        if is_valid:
            message = f"Income verified through ITR records"
        else:
            message = f"Income variance detected: {variance_percent:.1f}% difference"
        
        return is_valid, message, verification_result
    
    @staticmethod
    def comprehensive_verification(profile_data):
        """
        Run all verifications and return comprehensive report
        Returns: verification_report dict
        """
        report = {
            'overall_status': 'Pending',
            'verification_date': datetime.now().isoformat(),
            'verifications': {}
        }
        
        total_checks = 0
        passed_checks = 0
        
        # 1. PAN Verification
        if profile_data.get('pan_card'):
            is_valid, message, details = VerificationService.verify_pan_card(
                profile_data['pan_card'],
                profile_data.get('full_name', ''),
                profile_data.get('date_of_birth', '')
            )
            report['verifications']['pan'] = {
                'verified': is_valid,
                'message': message,
                'details': details
            }
            total_checks += 1
            if is_valid:
                passed_checks += 1
        
        # 2. Aadhar Verification
        if profile_data.get('aadhar_number'):
            is_valid, message, details = VerificationService.verify_aadhar(
                profile_data['aadhar_number'],
                profile_data.get('full_name', ''),
                profile_data.get('date_of_birth', '')
            )
            report['verifications']['aadhar'] = {
                'verified': is_valid,
                'message': message,
                'details': details
            }
            total_checks += 1
            if is_valid:
                passed_checks += 1
        
        # 3. Bank Account Verification
        if profile_data.get('account_number') and profile_data.get('ifsc_code'):
            is_valid, message, details = VerificationService.verify_bank_account(
                profile_data['account_number'],
                profile_data['ifsc_code'],
                profile_data.get('full_name', ''),
                profile_data.get('bank_name', '')
            )
            report['verifications']['bank_account'] = {
                'verified': is_valid,
                'message': message,
                'details': details
            }
            total_checks += 1
            if is_valid:
                passed_checks += 1
        
        # 4. CIBIL Score Verification
        if profile_data.get('cibil_score'):
            is_valid, actual_score, message, details = VerificationService.verify_cibil_score(
                profile_data.get('pan_card', ''),
                profile_data['cibil_score']
            )
            report['verifications']['cibil'] = {
                'verified': is_valid,
                'actual_score': actual_score,
                'message': message,
                'details': details
            }
            total_checks += 1
            if is_valid:
                passed_checks += 1
        
        # 5. Income Verification
        if profile_data.get('income_annum'):
            is_valid, message, details = VerificationService.verify_income(
                profile_data.get('pan_card', ''),
                profile_data['income_annum'],
                profile_data.get('employment_type', '')
            )
            report['verifications']['income'] = {
                'verified': is_valid,
                'message': message,
                'details': details
            }
            total_checks += 1
            if is_valid:
                passed_checks += 1
        
        # Calculate overall status
        if total_checks == 0:
            report['overall_status'] = 'No Data'
            report['verification_score'] = 0
        else:
            verification_score = (passed_checks / total_checks) * 100
            report['verification_score'] = round(verification_score, 2)
            report['checks_passed'] = passed_checks
            report['total_checks'] = total_checks
            
            if verification_score >= 80:
                report['overall_status'] = 'Verified'
            elif verification_score >= 60:
                report['overall_status'] = 'Partially Verified'
            else:
                report['overall_status'] = 'Verification Failed'
        
        return report


# Quick test function
if __name__ == '__main__':
    # Test PAN verification
    print("Testing PAN Verification:")
    is_valid, msg, details = VerificationService.verify_pan_card("ABCDE1234F", "John Doe", "1990-01-15")
    print(f"Valid: {is_valid}, Message: {msg}")
    print(f"Details: {details}\n")
    
    # Test Bank Account verification
    print("Testing Bank Account Verification:")
    is_valid, msg, details = VerificationService.verify_bank_account(
        "12345678901234", "SBIN0001234", "John Doe", "State Bank of India"
    )
    print(f"Valid: {is_valid}, Message: {msg}")
    print(f"Details: {details}\n")
    
    # Test CIBIL verification
    print("Testing CIBIL Verification:")
    is_valid, score, msg, details = VerificationService.verify_cibil_score("ABCDE1234F", 750)
    print(f"Valid: {is_valid}, Actual Score: {score}, Message: {msg}")
    print(f"Details: {details}\n")
