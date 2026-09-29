import joblib
import pandas as pd

from src.features.url_features import extract_features
from src.features.signals import generate_signals
from src.features.risk_score import calculate_risk_score


MODEL_PATH = "models/phishguard_model.joblib"
FEATURE_NAMES_PATH = "models/feature_names.txt"


# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------

model = joblib.load(MODEL_PATH)


# ---------------------------------------------------------
# Load exact feature order used during training
# ---------------------------------------------------------

with open(FEATURE_NAMES_PATH, "r") as file:
    feature_names = [
        line.strip()
        for line in file
        if line.strip()
    ]


# ---------------------------------------------------------
# Test URLs
# ---------------------------------------------------------

test_urls = [
    "https://www.google.com",
    "https://drive.google.com.evil-site.com/login",
    "http://192.168.1.10/login.php?user=admin&password=123",
]


# ---------------------------------------------------------
# Analyze URLs
# ---------------------------------------------------------

for url in test_urls:

    print("\n" + "=" * 70)
    print(f"URL: {url}")
    print("=" * 70)

    # -----------------------------------------------------
    # Extract features
    # -----------------------------------------------------

    features = extract_features(url)

    # -----------------------------------------------------
    # Build DataFrame using exact training feature order
    # -----------------------------------------------------

    feature_values = pd.DataFrame(
        [[features[name] for name in feature_names]],
        columns=feature_names,
    )

    # -----------------------------------------------------
    # ML prediction
    # -----------------------------------------------------

    probability = model.predict_proba(
        feature_values
    )[0][1]

    prediction = model.predict(
        feature_values
    )[0]

    # -----------------------------------------------------
    # Generate explainable signals
    # -----------------------------------------------------

    signals = generate_signals(features)

    # -----------------------------------------------------
    # Calculate risk score
    # -----------------------------------------------------

    risk = calculate_risk_score(
        features,
        probability,
        signals,
    )

    # -----------------------------------------------------
    # Display results
    # -----------------------------------------------------

    print(
        f"\nPrediction     : "
        f"{'PHISHING' if prediction == 1 else 'LEGITIMATE'}"
    )

    print(
        f"ML probability: "
        f"{probability:.4f}"
    )

    print(
        f"Risk score     : "
        f"{risk['score']}/100"
    )

    print(
        f"Risk level     : "
        f"{risk['level']}"
    )

    print(
        f"Signals        : "
        f"{risk['signals_count']}"
    )

    print("\nSignals:")

    if signals:

        for signal in signals:

            print(
                f"  [{signal['type'].upper()}] "
                f"{signal['title']}"
            )

            print(
                f"    {signal['description']}"
            )

    else:

        print("  None")