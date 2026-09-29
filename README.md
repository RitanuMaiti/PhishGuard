# PhishGuard

AI-assisted phishing URL detection system that combines machine learning, URL-structure analysis, rule-based security signals, and Gemini AI to assess suspicious URLs without loading the destination.

## Overview

PhishGuard analyzes a URL using multiple layers of detection:

1. **Machine Learning** — predicts the probability that a URL is phishing.
2. **URL Feature Extraction** — extracts structural characteristics such as domain length, subdomains, digits, hyphens, entropy, URL encoding, and suspicious keywords.
3. **Rule-Based Risk Analysis** — generates interpretable security signals from the URL structure.
4. **Gemini AI Analysis** — provides contextual analysis of the URL and can provide a different assessment when the ML model is overly confident.
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
* Suspicious URL characteristic detection
* URL feature extraction
* REST API using FastAPI
* React + Vite frontend
* QR-based URL input
* Analysis history
* Responsive investigation interface
* CORS-enabled frontend/backend communication
* Environment-variable based API key configuration

## Detection Pipeline

```text
                         User
                           |
                           v
                   React + Vite
                           |
                         HTTPS
                           |
                           v
                   FastAPI Backend
                           |
              +------------+------------+
              |            |            |
              v            v            v
             ML       Rule Engine   Gemini AI
              |            |            |
              +------------+------------+
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

The rule-based layer provides interpretable security signals based on characteristics found within the URL.

Gemini acts as an additional intelligence layer that evaluates the URL structure together with the locally generated analysis.

The AI layer is instructed to:

* Analyze only the supplied URL and local analysis data
* Avoid visiting, browsing, or resolving the destination
* Avoid inventing external information
* Treat HTTPS as a transport-security indicator rather than proof of legitimacy
* Consider suspicious URL structure, domain characteristics, subdomains, encoding, keywords, paths, queries, and other available evidence
* Provide an assessment even when it differs from the ML model

When Gemini is available, its assessment is given higher priority in determining the final prediction.

When Gemini is unavailable, PhishGuard falls back to its ML and rule-based analysis.

## Important Safety Design

PhishGuard does **not** load or visit the URL being analyzed.

The Gemini analysis is also instructed to reason only from:

* The URL itself
* Extracted URL features
* Rule-based signals
* ML output

It does not automatically rely on:

* WHOIS information
* DNS records
* Website contents
* Domain reputation
* Hosting information
* External blacklists
* Redirect chains

These properties are not assumed unless the relevant information is explicitly provided to the system.

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
* tldextract

### Frontend

* React
* Vite
* JavaScript
* CSS

### Deployment

* Netlify — frontend hosting
* Render — backend hosting
* GitHub — source control

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
* Login indicators
* Verification indicators
* Account indicators
* Security indicators
* Update indicators
* Payment indicators

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
├── .gitignore
├── requirements.txt
└── README.md
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

It is excluded through `.gitignore`.

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

> The example above illustrates the response structure. Actual values depend on the URL being analyzed.

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
* AI analysis being limited to the information supplied to the system

PhishGuard should therefore be treated as an additional security layer rather than a definitive source of truth.

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
