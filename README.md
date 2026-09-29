# PhishGuard

AI-assisted phishing URL detection system that combines machine learning, URL-structure analysis, rule-based signals, and Gemini AI to assess suspicious URLs without loading the destination.

## Overview

PhishGuard analyzes a URL using multiple layers of detection:

1. **Machine Learning** — predicts the probability that a URL is phishing.
2. **URL Feature Extraction** — extracts structural characteristics such as domain length, subdomains, digits, hyphens, entropy, URL encoding, and suspicious keywords.
3. **Rule-Based Risk Analysis** — generates interpretable security signals from the URL structure.
4. **Gemini AI Analysis** — provides contextual analysis of the URL and can identify cases where the ML model produces a false positive or false negative.
5. **Risk Fusion** — combines the available evidence, with the AI analysis given higher priority when available.
6. **React Frontend** — presents the final threat assessment, risk score, ML probability, and investigation signals.

PhishGuard is designed to analyze URLs **without visiting or loading the destination website**.

## Key Features

* AI-assisted phishing detection
* Machine-learning URL classification
* Gemini AI contextual analysis
* Rule-based security signals
* Risk score from 0–100
* Threat levels: LOW, MEDIUM, HIGH
* ML phishing probability
* Detection of suspicious URL characteristics
* URL feature extraction
* REST API using FastAPI
* React + Vite frontend
* QR-based URL input
* Analysis history
* Responsive investigation interface
* CORS-enabled frontend/backend communication
* API-key configuration through environment variables

## Detection Pipeline

```text
                    URL
                     |
                     v
            URL Feature Extraction
                     |
          +----------+----------+
          |                     |
          v                     v
     ML Classifier       Rule-Based Analysis
          |                     |
          |                     |
          +----------+----------+
                     |
                     v
               Gemini AI
             Analysis Layer
                     |
                     v
              Risk Fusion
                     |
                     v
             Final Assessment
                     |
                     v
              React Frontend
```

## AI + ML Approach

The ML model provides a statistical classification based on engineered URL features.

Gemini acts as an additional intelligence layer that evaluates the URL structure and the supplied local analysis data.

This allows PhishGuard to handle situations where the ML model may produce an overly confident prediction.

For example, during testing:

```text
URL: https://drive.google.com

ML phishing probability: 99.00%+
Gemini assessment:       Legitimate
Final detection:         LEGITIMATE
Final risk:              10/100
Risk level:              LOW
```

This demonstrates how the AI layer can provide contextual reasoning when the ML model produces a false positive.

## Important Safety Design

PhishGuard does **not** load or visit the URL being analyzed.

The Gemini analysis is also instructed to reason only from:

* The URL itself
* Extracted URL features
* Rule-based signals
* ML output

It does not rely on automatically browsing the destination.

Therefore, claims about external properties such as WHOIS information, DNS records, website contents, domain reputation, hosting information, or blacklist status are not assumed unless that information is explicitly provided to the system.

## Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Scikit-learn
* NumPy
* Pandas
* Joblib
* Pydantic
* Google Gemini API

### Frontend

* React
* Vite
* JavaScript
* CSS

### Machine Learning

The project uses engineered URL features including:

* URL length
* Domain length
* Path length
* Query length
* Number of subdomains
* Number of dots
* Number of hyphens
* Number of digits
* Special-character count
* IP address usage
* HTTPS usage
* URL encoding
* Digit/letter/special-character ratios
* Domain entropy
* Subdomain characteristics
* Numeric domains
* Suspicious keywords
* Login/verification/account/security/update/payment indicators

## Project Structure

```text
PhishGuard/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── main.jsx
│
├── models/
│   ├── feature_names.txt
│   ├── phishguard_model.joblib
│   └── phishguard_domain_holdout.joblib
│
├── notebooks/
│
├── src/
│   ├── api.py
│   ├── data/
│   ├── features/
│   ├── models/
│   └── utils/
│
├── tests/
│
├── .env
├── .gitignore
└── requirements.txt
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/RitanuMaiti/PhishGuard.git
cd PhishGuard
```

### 2. Create a Python virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file.

It is already excluded through `.gitignore`.

## Running the Backend

From the project root:

```powershell
python -m src.api
```

The FastAPI server runs at:

```text
http://127.0.0.1:8000
```

The analysis endpoint is:

```text
POST /api/analyze
```

Example request:

```json
{
  "url": "https://example.com"
}
```

## Running the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The Vite development server will provide a local URL, normally:

```text
http://localhost:5173/
```

Make sure the backend is running before analyzing URLs.

## API Response

A successful analysis returns information including:

```json
{
  "url": "https://example.com",
  "prediction": "legitimate",
  "ml_probability": 0.12,
  "phishing_probability": "12.00%",
  "risk_score": 15,
  "risk_level": "LOW",
  "signals": [],
  "signals_count": 0,
  "features": {},
  "ai_analysis": {
    "verdict": "legitimate",
    "confidence": 0.92,
    "risk_score": 5,
    "summary": "URL structure does not show obvious phishing indicators.",
    "signals": []
  },
  "ai_enabled": true
}
```

## Risk Levels

| Risk Score | Level  |
| ---------: | ------ |
|       0–29 | LOW    |
|      30–69 | MEDIUM |
|     70–100 | HIGH   |

The final risk score is generated from the available ML, rule-based, and AI analysis.

## Limitations

PhishGuard is an analysis and decision-support tool, not a guarantee of website safety.

URL structure alone cannot prove that a destination is malicious or legitimate.

Potential limitations include:

* ML false positives
* ML false negatives
* Ambiguous URLs
* Newly registered or unseen domains
* Lack of live domain reputation data
* Lack of DNS/WHOIS information
* Lack of webpage-content analysis
* Dependence on Gemini availability and quota

When Gemini is unavailable, PhishGuard falls back to its existing ML and rule-based analysis.

## Future Improvements

Potential future development includes:

* Domain reputation APIs
* DNS and WHOIS intelligence
* SSL certificate analysis
* Redirect-chain analysis
* Threat-intelligence feeds
* Browser-safe webpage inspection
* Improved model calibration
* Explainable ML analysis
* Continuous model evaluation
* Multimodal phishing analysis
* More comprehensive automated testing

## Disclaimer

PhishGuard is intended for educational, research, and defensive cybersecurity purposes.

Users should not rely solely on PhishGuard or any automated classifier when deciding whether to interact with a website.

## Author

**Ritanu Maiti**

B.Tech Computer Science and Engineering
Vellore Institute of Technology
