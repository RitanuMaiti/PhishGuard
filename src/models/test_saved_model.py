import joblib
import pandas as pd

from src.features.url_features import extract_features


MODEL_PATH = "models/phishguard_model.joblib"
FEATURES_PATH = "models/feature_names.txt"


def main():
    print("Loading model...")

    model = joblib.load(MODEL_PATH)

    with open(FEATURES_PATH, "r", encoding="utf-8") as file:
        feature_names = [line.strip() for line in file if line.strip()]

    test_urls = [
    "https://www.google.com",
    "https://drive.google.com/",
    "https://drive.google.com.evil-site.com/login",
    "https://secure-login.example.com/account/verify?id=123",
    "http://192.168.1.10/login.php?user=admin&password=123",
]

    print("\n=== PHISHGUARD TEST ===")

    for url in test_urls:
        features = extract_features(url)

        X = pd.DataFrame(
            [[features[name] for name in feature_names]],
            columns=feature_names,
        )

        probability = model.predict_proba(X)[0][1]
        prediction = int(probability >= 0.5)

        label = "PHISHING" if prediction == 1 else "LEGITIMATE"

        print("\nURL:")
        print(url)

        print(f"Prediction   : {label}")
        print(f"Probability  : {probability:.4f}")


if __name__ == "__main__":
    main()