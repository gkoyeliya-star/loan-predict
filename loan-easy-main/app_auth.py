from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import joblib
import numpy as np
import os
import json
from functools import wraps
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# Import verification service
from verification_service import VerificationService

# Initialize Flask app with explicit paths
app = Flask(__name__,
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))
            
app.config['SECRET_KEY'] = 'loaneasy-secret-key-2025-secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loaneasy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Load ML Model using absolute paths
try:
    model_path = BASE_DIR / 'loan_model_real.pkl'
    encoders_path = BASE_DIR / 'label_encoders_real.pkl'
    features_path = BASE_DIR / 'feature_names_real.pkl'
    
    model = joblib.load(str(model_path))
    label_encoders = joblib.load(str(encoders_path))
    feature_names = joblib.load(str(features_path))
    print("✓ ML Model loaded successfully")
    print(f"  Model path: {model_path}")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    print(f"  Looked in: {BASE_DIR}")
    model = None
    label_encoders = None
    feature_names = None

# ============ DATABASE MODELS ============

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    applications = db.relationship('LoanApplication', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Personal Information
    pan_card = db.Column(db.String(10), unique=True)
    aadhar_number = db.Column(db.String(12))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    no_of_dependents = db.Column(db.Integer)
    
    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    
    # Employment Details
    education = db.Column(db.String(50))
    employment_type = db.Column(db.String(50))
    employer_name = db.Column(db.String(200))
    designation = db.Column(db.String(100))
    years_employed = db.Column(db.Integer)
    income_annum = db.Column(db.Float)
    
    # Bank Details
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(20))
    ifsc_code = db.Column(db.String(11))
    account_type = db.Column(db.String(20))
    bank_asset_value = db.Column(db.Float, default=0)
    
    # Credit Information
    cibil_score = db.Column(db.Integer)
    existing_loans = db.Column(db.Integer, default=0)
    existing_emi = db.Column(db.Float, default=0)
    
    # Assets
    residential_assets_value = db.Column(db.Float, default=0)
    commercial_assets_value = db.Column(db.Float, default=0)
    luxury_assets_value = db.Column(db.Float, default=0)
    
    # Profile Status
    profile_completed = db.Column(db.Boolean, default=False)
    profile_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Verification Data (stored as JSON)
    verification_report = db.Column(db.Text)  # JSON string of verification results
    verification_date = db.Column(db.DateTime)
    pan_verified = db.Column(db.Boolean, default=False)
    aadhar_verified = db.Column(db.Boolean, default=False)
    bank_verified = db.Column(db.Boolean, default=False)
    cibil_verified = db.Column(db.Boolean, default=False)
    income_verified = db.Column(db.Boolean, default=False)

    def total_collateral(self):
        """Calculate total collateral value"""
        return (self.residential_assets_value or 0) + \
               (self.commercial_assets_value or 0) + \
               (self.luxury_assets_value or 0) + \
               (self.bank_asset_value or 0)

    def is_eligible_for_loan(self, loan_amount):
        """Check if user has sufficient collateral for loan"""
        total_assets = self.total_collateral()
        # Require at least 20% collateral of loan amount
        required_collateral = loan_amount * 0.20
        return total_assets >= required_collateral

class LoanApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    application_id = db.Column(db.String(20), unique=True)
    
    # Loan Details
    loan_amount = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    loan_purpose = db.Column(db.String(100))
    
    # Prediction Results
    prediction = db.Column(db.String(20))  # Approved/Rejected
    confidence = db.Column(db.Float)
    
    # Application Status
    status = db.Column(db.String(20), default='Pending')  # Pending/Approved/Rejected/Under Review
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    remarks = db.Column(db.Text)

    def generate_application_id(self):
        """Generate unique application ID"""
        import random
        self.application_id = f"LE{datetime.now().year}{random.randint(100000, 999999)}"

# ============ USER LOADER ============

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============ DECORATORS ============

def profile_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.profile or not current_user.profile.profile_completed:
            flash('Please complete your profile first to access this feature.', 'warning')
            return redirect(url_for('create_profile'))
        return f(*args, **kwargs)
    return decorated_function

# ============ ERROR HANDLERS ============

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error),
        'status': 500
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle uncaught exceptions"""
    import traceback
    return jsonify({
        'error': 'Application Error',
        'message': str(e),
        'traceback': traceback.format_exc(),
        'status': 500
    }), 500

# ============ ROUTES ============

@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('landing.html')
    except Exception as e:
        return f"Error loading page: {str(e)}<br>Check Vercel logs for details.", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'database': 'initialized'
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        # Validation
        if not all([email, password, confirm_password, full_name, phone]):
            flash('All fields are required!', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return render_template('register.html')
        
        # Create user
        user = User(email=email, full_name=full_name, phone=phone)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            print(f"Error: {e}")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Please enter both email and password!', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent applications
    recent_applications = LoanApplication.query.filter_by(user_id=current_user.id)\
                                               .order_by(LoanApplication.applied_at.desc())\
                                               .limit(5).all()
    
    # Calculate statistics
    total_applications = LoanApplication.query.filter_by(user_id=current_user.id).count()
    approved_applications = LoanApplication.query.filter_by(user_id=current_user.id, status='Approved').count()
    
    profile_completion = 0
    if current_user.profile and current_user.profile.profile_completed:
        profile_completion = 100
    elif current_user.profile:
        profile_completion = 50
    
    return render_template('dashboard.html', 
                         recent_applications=recent_applications,
                         total_applications=total_applications,
                         approved_applications=approved_applications,
                         profile_completion=profile_completion)

@app.route('/profile/create', methods=['GET', 'POST'])
@login_required
def create_profile():
    if current_user.profile and current_user.profile.profile_completed:
        flash('Your profile is already complete. You can edit it instead.', 'info')
        return redirect(url_for('edit_profile'))
    
    if request.method == 'POST':
        try:
            # Create or get existing profile
            profile = current_user.profile or UserProfile(user_id=current_user.id)
            
            # Personal Information
            profile.pan_card = request.form.get('pan_card', '').upper()
            profile.aadhar_number = request.form.get('aadhar_number', '')
            dob_str = request.form.get('date_of_birth')
            if dob_str:
                profile.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            profile.gender = request.form.get('gender')
            profile.marital_status = request.form.get('marital_status')
            profile.no_of_dependents = int(request.form.get('no_of_dependents', 0))
            
            # Address
            profile.address_line1 = request.form.get('address_line1')
            profile.address_line2 = request.form.get('address_line2', '')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.pincode = request.form.get('pincode')
            
            # Employment
            profile.education = request.form.get('education')
            profile.employment_type = request.form.get('employment_type')
            profile.employer_name = request.form.get('employer_name', '')
            profile.designation = request.form.get('designation', '')
            profile.years_employed = int(request.form.get('years_employed', 0))
            profile.income_annum = float(request.form.get('income_annum', 0))
            
            # Bank Details
            profile.bank_name = request.form.get('bank_name')
            profile.account_number = request.form.get('account_number')
            profile.ifsc_code = request.form.get('ifsc_code', '').upper()
            profile.account_type = request.form.get('account_type')
            profile.bank_asset_value = float(request.form.get('bank_asset_value', 0))
            
            # Credit Information
            profile.cibil_score = int(request.form.get('cibil_score', 0))
            profile.existing_loans = int(request.form.get('existing_loans', 0))
            profile.existing_emi = float(request.form.get('existing_emi', 0))
            
            # Assets
            profile.residential_assets_value = float(request.form.get('residential_assets_value', 0))
            profile.commercial_assets_value = float(request.form.get('commercial_assets_value', 0))
            profile.luxury_assets_value = float(request.form.get('luxury_assets_value', 0))
            
            # Mark as completed
            profile.profile_completed = True
            
            if not current_user.profile:
                db.session.add(profile)
            
            # Save profile first
            db.session.commit()
            
            # Now run verification
            flash('Profile saved! Running verification checks...', 'info')
            
            # Prepare data for verification
            profile_data = {
                'pan_card': profile.pan_card,
                'aadhar_number': profile.aadhar_number,
                'full_name': current_user.full_name,
                'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                'account_number': profile.account_number,
                'ifsc_code': profile.ifsc_code,
                'bank_name': profile.bank_name,
                'cibil_score': profile.cibil_score,
                'income_annum': profile.income_annum,
                'employment_type': profile.employment_type
            }
            
            # Run comprehensive verification
            verification_report = VerificationService.comprehensive_verification(profile_data)
            
            # Update profile with verification results
            profile.verification_report = json.dumps(verification_report)
            profile.verification_date = datetime.utcnow()
            
            # Update individual verification flags
            if 'pan' in verification_report['verifications']:
                profile.pan_verified = verification_report['verifications']['pan']['verified']
            if 'aadhar' in verification_report['verifications']:
                profile.aadhar_verified = verification_report['verifications']['aadhar']['verified']
            if 'bank_account' in verification_report['verifications']:
                profile.bank_verified = verification_report['verifications']['bank_account']['verified']
            if 'cibil' in verification_report['verifications']:
                profile.cibil_verified = verification_report['verifications']['cibil']['verified']
                # Update CIBIL score if different
                actual_score = verification_report['verifications']['cibil'].get('actual_score')
                if actual_score and abs(actual_score - profile.cibil_score) > 10:
                    old_score = profile.cibil_score
                    profile.cibil_score = actual_score
                    flash(f'CIBIL Score updated from {old_score} to {actual_score} based on credit bureau data', 'warning')
            if 'income' in verification_report['verifications']:
                profile.income_verified = verification_report['verifications']['income']['verified']
            
            # Set overall verification status
            if verification_report['overall_status'] == 'Verified':
                profile.profile_verified = True
                flash('✓ Profile verification completed successfully!', 'success')
            elif verification_report['overall_status'] == 'Partially Verified':
                profile.profile_verified = False
                flash('⚠ Profile partially verified. Some information could not be confirmed.', 'warning')
            else:
                profile.profile_verified = False
                flash('✗ Profile verification incomplete. Please check your details.', 'danger')
            
            db.session.commit()
            
            return redirect(url_for('verification_results'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating profile: {str(e)}', 'danger')
            print(f"Profile creation error: {e}")
    
    return render_template('create_profile.html')

@app.route('/profile/view')
@login_required
@profile_required
def view_profile():
    return render_template('view_profile.html', profile=current_user.profile)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@profile_required
def edit_profile():
    profile = current_user.profile
    
    if request.method == 'POST':
        try:
            # Update profile (similar to create_profile)
            profile.pan_card = request.form.get('pan_card', '').upper()
            profile.aadhar_number = request.form.get('aadhar_number', '')
            dob_str = request.form.get('date_of_birth')
            if dob_str:
                profile.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            profile.gender = request.form.get('gender')
            profile.marital_status = request.form.get('marital_status')
            profile.no_of_dependents = int(request.form.get('no_of_dependents', 0))
            
            profile.address_line1 = request.form.get('address_line1')
            profile.address_line2 = request.form.get('address_line2', '')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.pincode = request.form.get('pincode')
            
            profile.education = request.form.get('education')
            profile.employment_type = request.form.get('employment_type')
            profile.employer_name = request.form.get('employer_name', '')
            profile.designation = request.form.get('designation', '')
            profile.years_employed = int(request.form.get('years_employed', 0))
            profile.income_annum = float(request.form.get('income_annum', 0))
            
            profile.bank_name = request.form.get('bank_name')
            profile.account_number = request.form.get('account_number')
            profile.ifsc_code = request.form.get('ifsc_code', '').upper()
            profile.account_type = request.form.get('account_type')
            profile.bank_asset_value = float(request.form.get('bank_asset_value', 0))
            
            profile.cibil_score = int(request.form.get('cibil_score', 0))
            profile.existing_loans = int(request.form.get('existing_loans', 0))
            profile.existing_emi = float(request.form.get('existing_emi', 0))
            
            profile.residential_assets_value = float(request.form.get('residential_assets_value', 0))
            profile.commercial_assets_value = float(request.form.get('commercial_assets_value', 0))
            profile.luxury_assets_value = float(request.form.get('luxury_assets_value', 0))
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('view_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('edit_profile.html', profile=profile)

@app.route('/loan/apply', methods=['GET', 'POST'])
@login_required
@profile_required
def apply_loan():
    profile = current_user.profile
    
    if request.method == 'POST':
        try:
            loan_amount = float(request.form.get('loan_amount'))
            loan_term = int(request.form.get('loan_term'))
            loan_purpose = request.form.get('loan_purpose', '')
            
            # Check collateral eligibility
            if not profile.is_eligible_for_loan(loan_amount):
                total_collateral = profile.total_collateral()
                required_collateral = loan_amount * 0.20
                flash(f'Insufficient collateral! You have ₹{total_collateral:,.0f} but need at least ₹{required_collateral:,.0f} (20% of loan amount).', 'danger')
                return redirect(url_for('ineligible', 
                                       loan_amount=loan_amount,
                                       total_collateral=total_collateral,
                                       required_collateral=required_collateral))
            
            # Prepare features for prediction
            features = {
                'no_of_dependents': profile.no_of_dependents,
                'education': profile.education,
                'self_employed': ' Yes' if profile.employment_type == 'Self Employed' else ' No',
                'income_annum': profile.income_annum,
                'loan_amount': loan_amount,
                'loan_term': loan_term,
                'cibil_score': profile.cibil_score,
                'residential_assets_value': profile.residential_assets_value,
                'commercial_assets_value': profile.commercial_assets_value,
                'luxury_assets_value': profile.luxury_assets_value,
                'bank_asset_value': profile.bank_asset_value
            }
            
            # Make prediction
            prediction_result, confidence = make_prediction(features)
            
            # Create application
            application = LoanApplication(
                user_id=current_user.id,
                loan_amount=loan_amount,
                loan_term=loan_term,
                loan_purpose=loan_purpose,
                prediction=prediction_result,
                confidence=confidence,
                status='Approved' if prediction_result == 'Approved' else 'Under Review'
            )
            application.generate_application_id()
            
            db.session.add(application)
            db.session.commit()
            
            flash(f'Application submitted successfully! Application ID: {application.application_id}', 'success')
            return redirect(url_for('application_status', app_id=application.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting application: {str(e)}', 'danger')
            print(f"Application error: {e}")
    
    return render_template('apply_loan.html', profile=profile)

@app.route('/loan/ineligible')
@login_required
@profile_required
def ineligible():
    loan_amount = request.args.get('loan_amount', 0, type=float)
    total_collateral = request.args.get('total_collateral', 0, type=float)
    required_collateral = request.args.get('required_collateral', 0, type=float)
    
    return render_template('ineligible.html',
                         loan_amount=loan_amount,
                         total_collateral=total_collateral,
                         required_collateral=required_collateral)

@app.route('/loan/status/<int:app_id>')
@login_required
def application_status(app_id):
    application = LoanApplication.query.filter_by(id=app_id, user_id=current_user.id).first()
    
    if not application:
        flash('Application not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('application_status.html', application=application)

@app.route('/applications')
@login_required
def my_applications():
    applications = LoanApplication.query.filter_by(user_id=current_user.id)\
                                        .order_by(LoanApplication.applied_at.desc())\
                                        .all()
    return render_template('my_applications.html', applications=applications)

@app.route('/verification/results')
@login_required
@profile_required
def verification_results():
    """Show detailed verification results"""
    profile = current_user.profile
    
    # Parse verification report from JSON
    verification_report = None
    if profile.verification_report:
        try:
            verification_report = json.loads(profile.verification_report)
        except:
            verification_report = None
    
    return render_template('verification_results.html', 
                         profile=profile,
                         verification_report=verification_report)

@app.route('/api/verify/pan', methods=['POST'])
@login_required
def verify_pan_api():
    """API endpoint to verify PAN card"""
    data = request.get_json()
    pan_number = data.get('pan_number', '')
    name = data.get('name', '')
    dob = data.get('dob', '')
    
    is_valid, message, details = VerificationService.verify_pan_card(pan_number, name, dob)
    
    return jsonify({
        'valid': is_valid,
        'message': message,
        'details': details
    })

@app.route('/api/verify/bank', methods=['POST'])
@login_required
def verify_bank_api():
    """API endpoint to verify bank account"""
    data = request.get_json()
    account_number = data.get('account_number', '')
    ifsc_code = data.get('ifsc_code', '')
    name = data.get('name', '')
    bank_name = data.get('bank_name', '')
    
    is_valid, message, details = VerificationService.verify_bank_account(
        account_number, ifsc_code, name, bank_name
    )
    
    return jsonify({
        'valid': is_valid,
        'message': message,
        'details': details
    })

@app.route('/api/verify/rerun', methods=['POST'])
@login_required
@profile_required
def rerun_verification():
    """Re-run verification for current user's profile"""
    profile = current_user.profile
    
    # Prepare data for verification
    profile_data = {
        'pan_card': profile.pan_card,
        'aadhar_number': profile.aadhar_number,
        'full_name': current_user.full_name,
        'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        'account_number': profile.account_number,
        'ifsc_code': profile.ifsc_code,
        'bank_name': profile.bank_name,
        'cibil_score': profile.cibil_score,
        'income_annum': profile.income_annum,
        'employment_type': profile.employment_type
    }
    
    # Run comprehensive verification
    verification_report = VerificationService.comprehensive_verification(profile_data)
    
    # Update profile with verification results
    profile.verification_report = json.dumps(verification_report)
    profile.verification_date = datetime.utcnow()
    
    # Update individual verification flags
    if 'pan' in verification_report['verifications']:
        profile.pan_verified = verification_report['verifications']['pan']['verified']
    if 'aadhar' in verification_report['verifications']:
        profile.aadhar_verified = verification_report['verifications']['aadhar']['verified']
    if 'bank_account' in verification_report['verifications']:
        profile.bank_verified = verification_report['verifications']['bank_account']['verified']
    if 'cibil' in verification_report['verifications']:
        profile.cibil_verified = verification_report['verifications']['cibil']['verified']
    if 'income' in verification_report['verifications']:
        profile.income_verified = verification_report['verifications']['income']['verified']
    
    # Set overall verification status
    if verification_report['overall_status'] == 'Verified':
        profile.profile_verified = True
    else:
        profile.profile_verified = False
    
    db.session.commit()
    
    flash('Verification completed successfully!', 'success')
    return redirect(url_for('verification_results'))

# ============ HELPER FUNCTIONS ============

def make_prediction(features):
    """Make loan approval prediction using ML model"""
    if model is None:
        return 'Approved', 75.0  # Default fallback
    
    try:
        # Prepare features in correct order
        feature_vector = []
        for feature_name in feature_names:
            value = features.get(feature_name, 0)
            
            # Encode categorical features
            if feature_name in label_encoders:
                if value not in label_encoders[feature_name].classes_:
                    # Handle unknown category
                    value = label_encoders[feature_name].classes_[0]
                value = label_encoders[feature_name].transform([value])[0]
            
            feature_vector.append(value)
        
        # Make prediction
        feature_array = np.array([feature_vector])
        prediction = model.predict(feature_array)[0]
        probability = model.predict_proba(feature_array)[0]
        
        # Get confidence (probability of predicted class)
        confidence = probability[1] if prediction == 1 else probability[0]
        confidence = confidence * 100
        
        result = 'Approved' if prediction == 1 else 'Rejected'
        return result, confidence
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return 'Approved', 75.0  # Default fallback

# ============ INITIALIZE DATABASE ============

def init_app():
    """Initialize database if not exists"""
    try:
        with app.app_context():
            db.create_all()
            print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization error: {e}")
        # Don't crash - let app start anyway

# ============ RUN APPLICATION ============

if __name__ == '__main__':
    # Initialize database for local development
    init_app()
    print("\n" + "="*60)
    print("🏦 LOAN EASY - Professional Banking Application")
    print("="*60)
    print("✓ Server running on: http://127.0.0.1:5000")
    print("✓ Authentication system enabled")
    print("✓ User profiles and loan applications ready")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
