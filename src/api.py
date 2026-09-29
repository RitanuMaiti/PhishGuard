import os
import json
import time
from typing import List, Optional

import joblib
import numpy as np
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel, Field
from google import genai

from src.features.url_features import extract_features
from src.features.signals import generate_signals
from src.features.risk_score import calculate_risk_score


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"


# ============================================================
# GEMINI CLIENT
# ============================================================

gemini_client = None
GEMINI_AVAILABLE = False

try:
    if os.getenv("GEMINI_API_KEY"):
        gemini_client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        GEMINI_AVAILABLE = True
        print("[Gemini] Client initialized successfully.")
    else:
        print("[Gemini] GEMINI_API_KEY not found.")
except Exception as e:
    print(f"[Gemini] Client initialization failed: {e}")


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="PhishGuard",
    description="AI-assisted phishing URL detection API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOAD ML MODEL
# ============================================================

MODEL_PATH = "models/phishguard_model.joblib"
FEATURE_NAMES_PATH = "models/feature_names.txt"

model = None
feature_names = []

try:
    model = joblib.load(MODEL_PATH)
    print("[ML] Model loaded successfully.")
except Exception as e:
    print(f"[ML] Model loading failed: {e}")
    model = None

try:
    with open(FEATURE_NAMES_PATH, "r", encoding="utf-8") as f:
        feature_names = [
            line.strip()
            for line in f
            if line.strip()
        ]

    print(f"[ML] Loaded {len(feature_names)} feature names.")
except Exception as e:
    print(f"[ML] Feature names loading failed: {e}")
    feature_names = []


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class URLRequest(BaseModel):
    url: str


class AISignal(BaseModel):
    title: str
    description: str
    severity: str


class AIAnalysis(BaseModel):
    verdict: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: int = Field(ge=0, le=100)
    summary: str
    signals: List[AISignal]


# ============================================================
# HELPERS
# ============================================================

def clean_json_response(text: str) -> str:
    """
    Removes markdown code fences if Gemini returns JSON
    inside ```json ... ``` blocks.
    """

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


# ============================================================
# GEMINI ANALYSIS
# ============================================================

def analyze_with_ai(
    url: str,
    features: dict,
    ml_probability: float,
    base_risk_score: int,
    existing_signals: dict
) -> Optional[AIAnalysis]:

    if not GEMINI_AVAILABLE or gemini_client is None:
        print("[Gemini] AI unavailable.")
        return None

    prompt = f"""
You are the primary intelligence layer of a phishing URL detection system.

Analyze ONLY the URL string and the provided local analysis data.

IMPORTANT SECURITY RULES:

1. DO NOT browse, fetch, open, resolve, or visit the URL.

2. DO NOT claim facts about DNS, WHOIS, SSL certificates,
   domain age, IP reputation, blacklists, hosting, redirects,
   webpage contents, or external reputation unless those facts
   are explicitly provided in the input.

3. HTTPS means encrypted transport. HTTPS alone does NOT prove
   that a website is legitimate.

4. Do not automatically agree with the machine-learning model.

5. The ML prediction is only supporting evidence.

6. URL structure alone cannot prove that a URL is malicious or safe.

7. If evidence is ambiguous, prefer "suspicious" rather than
   confidently calling the URL legitimate.

8. Do not invent evidence.

9. Consider that legitimate services may use subdomains.

10. A subdomain by itself is NOT evidence of phishing.

Your role is to provide the PRIMARY assessment.

URL:
{url}

Machine-learning phishing probability:
{ml_probability:.4f}

Existing rule-based risk score:
{base_risk_score}

Extracted URL features:
{json.dumps(features, indent=2)}

Existing security signals:
{json.dumps(existing_signals, indent=2)}

Consider factors such as:

- suspicious domain structure
- excessive or unusual subdomains
- unusual domain length
- excessive digits
- excessive hyphens
- encoded characters
- IP address usage
- suspicious words
- login/account/payment/verify/update terminology
- suspicious paths
- suspicious query parameters
- unusually long URLs
- unusual character patterns
- mismatch between domain structure and apparent brand identity
- whether the ML prediction appears consistent with the URL structure

IMPORTANT:

The ML model is supporting evidence, NOT the final authority.

A legitimate well-known service can have subdomains.

Do not classify a URL as phishing merely because it has a subdomain.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
    "verdict": "phishing" | "legitimate" | "suspicious",
    "confidence": 0.0,
    "risk_score": 0,
    "summary": "short explanation",
    "signals": [
        {{
            "title": "signal title",
            "description": "explanation",
            "severity": "LOW" | "MEDIUM" | "HIGH"
        }}
    ]
}}

Confidence must be between 0 and 1.

Risk score must be between 0 and 100.

Do not include markdown.

Do not include additional fields.
"""

    # ========================================================
    # GEMINI REQUEST WITH RETRY
    # ========================================================

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            print(
                f"[Gemini] Sending analysis request "
                f"(attempt {attempt}/{max_attempts})..."
            )

            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            print("[Gemini] Response received.")

            raw_response = response.text.strip()

            print("[Gemini] Raw response:")
            print(raw_response)

            cleaned_response = clean_json_response(raw_response)

            parsed = json.loads(cleaned_response)

            analysis = AIAnalysis.model_validate(parsed)

            print(
                f"[Gemini] Verdict: {analysis.verdict} | "
                f"Confidence: {analysis.confidence:.2f} | "
                f"Risk: {analysis.risk_score}"
            )

            return analysis

        except Exception as e:
            error_text = str(e)

            print(
                f"[Gemini] Attempt {attempt} failed: "
                f"{error_text}"
            )

            if "503" in error_text and attempt < max_attempts:
                wait_seconds = attempt

                print(
                    f"[Gemini] Service temporarily unavailable. "
                    f"Retrying in {wait_seconds} second(s)..."
                )

                time.sleep(wait_seconds)
                continue

            print("[Gemini] AI analysis unavailable.")
            return None

    return None


# ============================================================
# GEMINI + ML FUSION
# ============================================================

def calculate_final_risk(
    ml_probability: float,
    base_risk_score: int,
    ai_analysis: Optional[AIAnalysis]
) -> int:

    # --------------------------------------------------------
    # No AI -> use existing ML/rule system
    # --------------------------------------------------------

    if ai_analysis is None:
        return max(
            0,
            min(
                100,
                int(round(base_risk_score))
            )
        )

    # --------------------------------------------------------
    # Gemini is the PRIMARY layer.
    #
    # Base weighting:
    # Gemini = 70%
    # ML     = 30%
    #
    # Confidence can slightly increase Gemini influence.
    # --------------------------------------------------------

    ai_confidence = max(
        0.0,
        min(
            1.0,
            ai_analysis.confidence
        )
    )

    # Gemini influence ranges approximately from 70% to 85%.
    ai_weight = 0.70 + (0.15 * ai_confidence)

    # ML gets the remaining influence.
    ml_weight = 1.0 - ai_weight

    ai_score = float(ai_analysis.risk_score)
    ml_score = float(base_risk_score)

    fused_score = (
        (ai_score * ai_weight)
        + (ml_score * ml_weight)
    )

    # --------------------------------------------------------
    # Verdict-aware adjustment
    # --------------------------------------------------------

    if ai_analysis.confidence >= 0.85:

        if ai_analysis.verdict == "legitimate":
            fused_score = min(
                fused_score,
                ai_score + 10
            )

        elif ai_analysis.verdict == "phishing":
            fused_score = max(
                fused_score,
                ai_score - 10
            )

    return max(
        0,
        min(
            100,
            int(round(fused_score))
        )
    )


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(score: int) -> str:

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "PhishGuard",
        "status": "online",
        "message": "Phishing URL detection API",
        "ai_enabled": GEMINI_AVAILABLE
    }


# ============================================================
# ANALYZE URL
# ============================================================

@app.post("/api/analyze")
def analyze_url(request: URLRequest):

    url = request.url.strip()

    # --------------------------------------------------------
    # Feature extraction
    # --------------------------------------------------------

    try:
        features = extract_features(url)

    except Exception as e:
        return {
            "error": f"Feature extraction failed: {str(e)}"
        }

    # --------------------------------------------------------
    # ML prediction
    # --------------------------------------------------------

    ml_probability = 0.0
    prediction = "unknown"

    if model is not None:

        try:
            # Preserve exact feature order used during training.
            feature_vector = [
                safe_float(
                    features.get(name, 0.0)
                )
                for name in feature_names
            ]

            X = np.array(
                [feature_vector],
                dtype=float
            )

            probabilities = model.predict_proba(X)[0]

            # Assumes class 1 = phishing.
            ml_probability = float(
                probabilities[1]
            )

            prediction = (
                "phishing"
                if ml_probability >= 0.5
                else "legitimate"
            )

        except Exception as e:

            print(
                f"[ML] Prediction failed: {e}"
            )

            ml_probability = 0.0
            prediction = "unknown"

    # --------------------------------------------------------
    # Rule-based signals
    # --------------------------------------------------------

    try:
        signals = generate_signals(
            url,
            features
        )

    except TypeError:

        try:
            signals = generate_signals(
                features
            )

        except Exception:
            signals = {}

    except Exception as e:

        print(
            f"[Signals] Generation failed: {e}"
        )

        signals = {}

    # --------------------------------------------------------
    # Existing/base risk score
    # --------------------------------------------------------

    try:
        base_risk_score = calculate_risk_score(
            ml_probability,
            signals
        )

    except TypeError:

        try:
            base_risk_score = calculate_risk_score(
                ml_probability
            )

        except Exception:
            base_risk_score = int(
                round(
                    ml_probability * 100
                )
            )

    except Exception as e:

        print(
            f"[Risk] Calculation failed: {e}"
        )

        base_risk_score = int(
            round(
                ml_probability * 100
            )
        )

    base_risk_score = max(
        0,
        min(
            100,
            int(
                round(
                    safe_float(
                        base_risk_score
                    )
                )
            )
        )
    )

    # --------------------------------------------------------
    # Gemini AI analysis
    # --------------------------------------------------------

    ai_analysis = analyze_with_ai(
        url=url,
        features=features,
        ml_probability=ml_probability,
        base_risk_score=base_risk_score,
        existing_signals=signals
    )

    # --------------------------------------------------------
    # Final fused score
    # --------------------------------------------------------

    final_risk_score = calculate_final_risk(
        ml_probability=ml_probability,
        base_risk_score=base_risk_score,
        ai_analysis=ai_analysis
    )

    risk_level = get_risk_level(
        final_risk_score
    )

    # --------------------------------------------------------
    # Final prediction
    #
    # Gemini is primary here.
    # --------------------------------------------------------

    if ai_analysis is not None:

        if ai_analysis.verdict == "phishing":
            final_prediction = "phishing"

        elif ai_analysis.verdict == "suspicious":
            final_prediction = "suspicious"

        else:
            final_prediction = "legitimate"

    else:
        final_prediction = prediction

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "url": url,

        "prediction": final_prediction,

        "ml_probability": round(
            ml_probability,
            4
        ),

        "phishing_probability": (
            f"{ml_probability * 100:.2f}%"
        ),

        "risk_score": final_risk_score,

        "risk_level": risk_level,

        "signals": signals,

        "signals_count": (
            len(signals)
            if isinstance(
                signals,
                (dict, list)
            )
            else 0
        ),

        "features": features,

        "ai_analysis": (
            ai_analysis.model_dump()
            if ai_analysis is not None
            else None
        ),

        "ai_enabled": GEMINI_AVAILABLE
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )