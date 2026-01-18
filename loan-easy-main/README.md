# 🏦 Loan Eligibility Checker - AI-Powered

A streamlined, stateless loan eligibility prediction system powered by machine learning. Get instant loan approval predictions with confidence scores.

## ✨ Features

- **Instant Predictions**: Real-time loan eligibility checking using AI
- **No Registration**: Simple, stateless application - no user accounts needed
- **95%+ Accuracy**: Trained on 10,000+ synthetic loan applications
- **Modern UI**: Beautiful, mobile-responsive interface with smooth animations
- **Explainable AI**: Confidence scores show prediction reliability

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Anamitra-Sarkar/loan-predict.git
   cd loan-predict/loan-easy-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

### Deployment on Render

1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically use `render.yaml` for configuration
4. The app will be live at your Render URL

## 🤖 Machine Learning Model

### Model Details
- **Algorithm**: Gradient Boosting Classifier
- **Accuracy**: 95.35%
- **Cross-Validation Score**: 95.16%
- **Training Data**: 10,000 synthetic loan applications
- **Python Version**: 3.11
- **scikit-learn**: 1.3.2

### Features Used
The model considers 11 features for prediction:

| Feature | Description | Importance |
|---------|-------------|------------|
| Credit_History | Payment history (0=Poor, 1=Good) | 71.66% |
| ApplicantIncome | Primary applicant's monthly income | 10.11% |
| CoapplicantIncome | Co-applicant's monthly income | 6.62% |
| LoanAmount | Requested loan amount (in $1000s) | 5.68% |
| Property_Area | Urban/Semiurban/Rural | 1.57% |
| Married | Marital status | 1.51% |
| Education | Graduate/Not Graduate | 0.85% |
| Dependents | Number of dependents (0/1/2/3+) | 0.80% |
| Loan_Amount_Term | Repayment period in months | 0.75% |
| Gender | Male/Female | 0.25% |
| Self_Employed | Employment type | 0.20% |

### Key Insights
- **Credit history** is the strongest predictor (72% importance)
- **Income-to-loan ratio** significantly affects approval
- **Total household income** matters more than individual income
- **Education** and **marital status** have minor positive effects

## 📁 Project Structure

```
loan-easy-main/
├── app.py                          # Main Flask application (stateless)
├── wsgi.py                         # WSGI entry point for Gunicorn
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render deployment config
├── runtime.txt                     # Python version specification
├── build.sh                        # Build script for deployment
│
├── Models/                         # ML model artifacts
│   ├── loan_model_real.pkl         # Trained GradientBoosting model
│   ├── label_encoders_real.pkl     # Categorical encoders
│   ├── feature_names_real.pkl      # Feature names in order
│   └── model_info_real.txt         # Model metadata
│
├── templates/                      # HTML templates
│   └── index.html                  # Main application page
│
├── static/                         # Static files (CSS/JS/Images)
│
├── generate_synthetic_data.py      # Data generation script
├── train_new_model.py              # Model training script
└── README.md                       # This file
```

## 🎨 User Interface

### Design Features
- **Gradient Background**: Beautiful purple gradient
- **Floating Icons**: Animated bank and money icons in background
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop
- **Smooth Animations**: Professional transitions and effects
- **Clean Forms**: Easy-to-use input fields with validation
- **Real-time Feedback**: Loading animations and result displays

### Mobile Responsive
- Optimized layouts for screens from 320px to 4K
- Touch-friendly controls
- Readable fonts and proper spacing
- Fast loading times

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11, Flask 3.0 |
| **ML Framework** | scikit-learn 1.3.2 |
| **Numerical Computing** | NumPy 1.26.4 |
| **Model Serialization** | Joblib 1.5.3 |
| **Web Server** | Gunicorn |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Icons** | Font Awesome 6.4 |
| **Deployment** | Render |

## 🎯 How to Use

1. **Fill in Personal Information**
   - Gender, marital status, dependents
   - Education level, employment type
   - Property area

2. **Provide Financial Details**
   - Your monthly income
   - Co-applicant's income (if applicable)

3. **Enter Loan Details**
   - Desired loan amount (in thousands)
   - Preferred loan term (months)
   - Credit history status

4. **Get Instant Results**
   - Approval/rejection prediction
   - Confidence score (0-100%)
   - AI-powered analysis

## 📊 Example Scenarios

### High Approval Chance
```
Income: $7,000/month
Co-applicant: $2,000/month
Loan: $150,000 (30 years)
Credit History: Good
→ Result: ✅ Likely Approved (99%+ confidence)
```

### Medium Approval Chance
```
Income: $4,000/month
Co-applicant: $0
Loan: $200,000 (15 years)
Credit History: Good
→ Result: Review needed (60-80% confidence)
```

### Low Approval Chance
```
Income: $3,000/month
Co-applicant: $0
Loan: $300,000 (30 years)
Credit History: Poor
→ Result: ❌ Likely Rejected (90%+ confidence)
```

## 🛠️ Development

### Training a New Model

1. **Generate synthetic data** (customizable)
   ```bash
   python generate_synthetic_data.py
   ```

2. **Train the model**
   ```bash
   python train_new_model.py
   ```

3. **Verify model artifacts** in `Models/` directory
   - loan_model_real.pkl
   - label_encoders_real.pkl
   - feature_names_real.pkl

### Customizing the Model

Edit `generate_synthetic_data.py` to adjust:
- Number of samples
- Feature distributions
- Approval logic rules

Edit `train_new_model.py` to modify:
- Model type (GradientBoosting vs RandomForest)
- Hyperparameters
- Training/test split ratio

## 🔒 Security & Privacy

- **No Data Storage**: All predictions are stateless
- **No User Tracking**: No cookies, sessions, or accounts
- **No Database**: Zero persistence of user information
- **Privacy-First**: Your data never leaves the prediction request

## 🚀 Performance

- **Fast Predictions**: < 100ms response time
- **Lightweight**: ~5MB total application size
- **Scalable**: Stateless design allows horizontal scaling
- **Reliable**: 99%+ uptime on Render free tier

## 📝 Environment Variables

For production deployment, set these in your Render dashboard:

```bash
PYTHON_VERSION=3.11.0
SECRET_KEY=your-secret-key-here  # Auto-generated by Render
FLASK_ENV=production
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:5000/health
```

### Prediction API Test
```bash
curl -X POST http://localhost:5000/predict \
  -F "applicant_income=5000" \
  -F "coapplicant_income=2000" \
  -F "loan_amount=150" \
  -F "loan_term=360" \
  -F "credit_history=1" \
  -F "gender=Male" \
  -F "married=Yes" \
  -F "dependents=0" \
  -F "education=Graduate" \
  -F "self_employed=No" \
  -F "property_area=Urban"
```

## 🐛 Troubleshooting

### Model Not Loading
```bash
# Retrain the model
python train_new_model.py
```

### Port Already in Use
```bash
# Use a different port
python app.py --port 5001
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt
```

## 📈 Future Enhancements

- [ ] Export prediction results as PDF
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] EMI calculator integration
- [ ] Comparison with different loan terms
- [ ] Historical data visualization
- [ ] Mobile app (React Native/Flutter)

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

## 🌟 Acknowledgments

- Built with Flask and scikit-learn
- Deployed on Render
- Icons by Font Awesome

---

**Made with ❤️ for better financial accessibility**

🏦 **Empowering Smart Lending Decisions**
