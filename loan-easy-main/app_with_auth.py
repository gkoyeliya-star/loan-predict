from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import joblib
import numpy as np
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loaneasy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Load ML model
try:
    model = joblib.load('loan_model_real.pkl')
    label_encoders = joblib.load('label_encoders_real.pkl')
    feature_names = joblib.load('feature_names_real.pkl')
    print(f"✓ Model loaded: {type(model).__name__}")
    print(f"✓ Features: {feature_names}")
except Exception as e:
    print(f"Warning: Could not load model - {e}")
    model = None

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to profile
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    loan_applications = db.relationship('LoanApplication', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Personal Information
    full_name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    
    # Identity Documents
    pan_card = db.Column(db.String(10), unique=True, nullable=False)
    aadhar_card = db.Column(db.String(12), unique=True, nullable=False)
    
    # Address
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    
    # Employment Information
    employment_type = db.Column(db.String(50), nullable=False)  # Salaried/Self-Employed
    occupation = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(200))
    annual_income = db.Column(db.Float, nullable=False)
    
    # Education
    education_level = db.Column(db.String(50), nullable=False)  # Graduate/Not Graduate
    
    # Family Information
    marital_status = db.Column(db.String(20), nullable=False)
    no_of_dependents = db.Column(db.Integer, default=0)
    
    # Bank Details
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    ifsc_code = db.Column(db.String(11), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # Savings/Current
    bank_balance = db.Column(db.Float, default=0)
    
    # Credit Information
    cibil_score = db.Column(db.Integer, nullable=False)
    existing_loans = db.Column(db.Integer, default=0)
    total_emi = db.Column(db.Float, default=0)
    
    # Assets/Collateral
    residential_property_value = db.Column(db.Float, default=0)
    commercial_property_value = db.Column(db.Float, default=0)
    vehicle_value = db.Column(db.Float, default=0)
    luxury_assets_value = db.Column(db.Float, default=0)
    gold_value = db.Column(db.Float, default=0)
    
    # Profile Status
    is_complete = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def total_collateral(self):
        """Calculate total collateral value"""
        return (
            (self.residential_property_value or 0) +
            (self.commercial_property_value or 0) +
            (self.vehicle_value or 0) +
            (self.luxury_assets_value or 0) +
            (self.gold_value or 0) +
            (self.bank_balance or 0)
        )
    
    @property
    def is_eligible_for_loan(self):
        """Check if user meets minimum collateral requirements"""
        MIN_COLLATERAL = 500000  # Minimum 5 lakhs in collateral
        MIN_CIBIL = 300  # Minimum CIBIL score
        
        return (
            self.total_collateral >= MIN_COLLATERAL and
            self.cibil_score >= MIN_CIBIL and
            self.is_complete
        )
    
    @property
    def max_eligible_loan(self):
        """Calculate maximum eligible loan amount"""
        # Conservative estimate: 60% of total collateral
        return self.total_collateral * 0.6


class LoanApplication(db.Model):
    __tablename__ = 'loan_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    application_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Loan Details
    loan_amount = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)  # in months
    loan_purpose = db.Column(db.String(200), nullable=False)
    
    # Prediction Results
    prediction = db.Column(db.String(20))  # Approved/Rejected
    confidence_score = db.Column(db.Float)
    
    # Application Status
    status = db.Column(db.String(50), default='Pending')  # Pending/Approved/Rejected/Under Review
    
    # Timestamps
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Admin Notes
    admin_notes = db.Column(db.Text)


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def index():
    """Home page - redirect based on login status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        
        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please complete your profile.', 'success')
        login_user(new_user)
        return redirect(url_for('create_profile'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Login successful!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    profile = current_user.profile
    
    # Get recent loan applications
    applications = LoanApplication.query.filter_by(user_id=current_user.id).order_by(
        LoanApplication.applied_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html', profile=profile, applications=applications)


@app.route('/profile/create', methods=['GET', 'POST'])
@login_required
def create_profile():
    """Create user profile"""
    # Check if profile already exists
    if current_user.profile and current_user.profile.is_complete:
        flash('Profile already exists. You can edit it from your dashboard.', 'info')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            # Create or update profile
            profile = current_user.profile
            if not profile:
                profile = UserProfile(user_id=current_user.id)
            
            # Personal Information
            profile.full_name = request.form.get('full_name')
            profile.phone_number = request.form.get('phone_number')
            profile.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            profile.gender = request.form.get('gender')
            
            # Identity
            profile.pan_card = request.form.get('pan_card').upper()
            profile.aadhar_card = request.form.get('aadhar_card')
            
            # Address
            profile.address_line1 = request.form.get('address_line1')
            profile.address_line2 = request.form.get('address_line2', '')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.pincode = request.form.get('pincode')
            
            # Employment
            profile.employment_type = request.form.get('employment_type')
            profile.occupation = request.form.get('occupation')
            profile.company_name = request.form.get('company_name', '')
            profile.annual_income = float(request.form.get('annual_income'))
            
            # Education
            profile.education_level = request.form.get('education_level')
            
            # Family
            profile.marital_status = request.form.get('marital_status')
            profile.no_of_dependents = int(request.form.get('no_of_dependents', 0))
            
            # Bank Details
            profile.bank_name = request.form.get('bank_name')
            profile.account_number = request.form.get('account_number')
            profile.ifsc_code = request.form.get('ifsc_code').upper()
            profile.account_type = request.form.get('account_type')
            profile.bank_balance = float(request.form.get('bank_balance', 0))
            
            # Credit Information
            profile.cibil_score = int(request.form.get('cibil_score'))
            profile.existing_loans = int(request.form.get('existing_loans', 0))
            profile.total_emi = float(request.form.get('total_emi', 0))
            
            # Assets
            profile.residential_property_value = float(request.form.get('residential_property_value', 0))
            profile.commercial_property_value = float(request.form.get('commercial_property_value', 0))
            profile.vehicle_value = float(request.form.get('vehicle_value', 0))
            profile.luxury_assets_value = float(request.form.get('luxury_assets_value', 0))
            profile.gold_value = float(request.form.get('gold_value', 0))
            
            # Mark as complete
            profile.is_complete = True
            
            db.session.add(profile)
            db.session.commit()
            
            flash('Profile created successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating profile: {str(e)}', 'danger')
    
    return render_template('create_profile.html')


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    profile = current_user.profile
    
    if not profile:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('create_profile'))
    
    if request.method == 'POST':
        try:
            # Update profile (same logic as create)
            profile.full_name = request.form.get('full_name')
            profile.phone_number = request.form.get('phone_number')
            profile.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            profile.gender = request.form.get('gender')
            
            profile.pan_card = request.form.get('pan_card').upper()
            profile.aadhar_card = request.form.get('aadhar_card')
            
            profile.address_line1 = request.form.get('address_line1')
            profile.address_line2 = request.form.get('address_line2', '')
            profile.city = request.form.get('city')
            profile.state = request.form.get('state')
            profile.pincode = request.form.get('pincode')
            
            profile.employment_type = request.form.get('employment_type')
            profile.occupation = request.form.get('occupation')
            profile.company_name = request.form.get('company_name', '')
            profile.annual_income = float(request.form.get('annual_income'))
            
            profile.education_level = request.form.get('education_level')
            
            profile.marital_status = request.form.get('marital_status')
            profile.no_of_dependents = int(request.form.get('no_of_dependents', 0))
            
            profile.bank_name = request.form.get('bank_name')
            profile.account_number = request.form.get('account_number')
            profile.ifsc_code = request.form.get('ifsc_code').upper()
            profile.account_type = request.form.get('account_type')
            profile.bank_balance = float(request.form.get('bank_balance', 0))
            
            profile.cibil_score = int(request.form.get('cibil_score'))
            profile.existing_loans = int(request.form.get('existing_loans', 0))
            profile.total_emi = float(request.form.get('total_emi', 0))
            
            profile.residential_property_value = float(request.form.get('residential_property_value', 0))
            profile.commercial_property_value = float(request.form.get('commercial_property_value', 0))
            profile.vehicle_value = float(request.form.get('vehicle_value', 0))
            profile.luxury_assets_value = float(request.form.get('luxury_assets_value', 0))
            profile.gold_value = float(request.form.get('gold_value', 0))
            
            profile.is_complete = True
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('edit_profile.html', profile=profile)


@app.route('/apply-loan', methods=['GET', 'POST'])
@login_required
def apply_loan():
    """Apply for a loan"""
    profile = current_user.profile
    
    # Check if profile exists and is complete
    if not profile or not profile.is_complete:
        flash('Please complete your profile before applying for a loan.', 'warning')
        return redirect(url_for('create_profile'))
    
    # Check eligibility based on collateral
    if not profile.is_eligible_for_loan:
        total_collateral = profile.total_collateral
        flash(f'Insufficient collateral. You have ₹{total_collateral:,.0f} in assets. Minimum required: ₹5,00,000. Please update your profile with property or asset details.', 'danger')
        return render_template('ineligible.html', profile=profile)
    
    if request.method == 'POST':
        try:
            loan_amount = float(request.form.get('loan_amount'))
            loan_term = int(request.form.get('loan_term'))
            loan_purpose = request.form.get('loan_purpose')
            
            # Validate loan amount against max eligible
            max_eligible = profile.max_eligible_loan
            if loan_amount > max_eligible:
                flash(f'Loan amount exceeds maximum eligible amount of ₹{max_eligible:,.0f}. Please reduce the amount.', 'warning')
                return render_template('apply_loan.html', profile=profile)
            
            # Prepare data for ML model
            feature_data = {
                'no_of_dependents': profile.no_of_dependents,
                'education': ' Graduate' if profile.education_level == 'Graduate' else ' Not Graduate',
                'self_employed': ' Yes' if profile.employment_type == 'Self-Employed' else ' No',
                'income_annum': profile.annual_income,
                'loan_amount': loan_amount,
                'loan_term': loan_term,
                'cibil_score': profile.cibil_score,
                'residential_assets_value': profile.residential_property_value,
                'commercial_assets_value': profile.commercial_property_value,
                'luxury_assets_value': profile.luxury_assets_value + profile.vehicle_value,
                'bank_asset_value': profile.bank_balance
            }
            
            # Make prediction
            if model:
                # Encode categorical features
                for feature in ['education', 'self_employed']:
                    if feature in label_encoders:
                        feature_data[feature] = label_encoders[feature].transform([feature_data[feature]])[0]
                
                # Create feature array in correct order
                X = np.array([[feature_data[f] for f in feature_names]])
                
                # Get prediction
                prediction = model.predict(X)[0]
                prediction_proba = model.predict_proba(X)[0]
                confidence = prediction_proba[1] * 100  # Probability of approval
                
                prediction_text = 'Approved' if prediction == 1 else 'Rejected'
            else:
                # Fallback if model not loaded
                prediction_text = 'Approved'
                confidence = 85.0
            
            # Generate application number
            app_number = f"LE{datetime.now().strftime('%Y%m%d')}{current_user.id:04d}{LoanApplication.query.count() + 1:04d}"
            
            # Create loan application
            application = LoanApplication(
                user_id=current_user.id,
                application_number=app_number,
                loan_amount=loan_amount,
                loan_term=loan_term,
                loan_purpose=loan_purpose,
                prediction=prediction_text,
                confidence_score=confidence,
                status='Pending' if prediction_text == 'Approved' else 'Under Review'
            )
            
            db.session.add(application)
            db.session.commit()
            
            flash(f'Application submitted successfully! Application Number: {app_number}', 'success')
            return redirect(url_for('application_status', app_id=application.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting application: {str(e)}', 'danger')
    
    return render_template('apply_loan.html', profile=profile)


@app.route('/application/<int:app_id>')
@login_required
def application_status(app_id):
    """View loan application status"""
    application = LoanApplication.query.get_or_404(app_id)
    
    # Ensure user owns this application
    if application.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('application_status.html', application=application)


@app.route('/my-applications')
@login_required
def my_applications():
    """View all loan applications"""
    applications = LoanApplication.query.filter_by(user_id=current_user.id).order_by(
        LoanApplication.applied_at.desc()
    ).all()
    
    return render_template('my_applications.html', applications=applications)


# Initialize database
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully!")


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run app
    print("\n" + "="*60)
    print("🏦 LOAN EASY - Banking Application with Authentication")
    print("="*60)
    print("\n✓ Server starting on http://127.0.0.1:5000")
    print("✓ Features:")
    print("  - User Registration & Login")
    print("  - Complete Profile Management")
    print("  - Collateral-based Loan Eligibility")
    print("  - ML-powered Loan Predictions")
    print("  - Application Tracking\n")
    
    app.run(debug=True, port=5000)
