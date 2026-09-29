import joblib
import pandas as pd

from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split


DATA_PATH = Path("data/processed/url_features.csv")
MODEL_PATH = Path("models/phishguard_model.joblib")
FEATURES_PATH = Path("models/feature_names.txt")


def main():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    # Remove duplicate feature patterns
    df = df.drop_duplicates()

    X = df.drop(columns=["label"])
    y = df["label"]

    print(f"Training rows: {len(X):,}")
    print(f"Features: {len(X.columns)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("\nTraining final Hist Gradient Boosting model...")

    model = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.1,
        random_state=42,
    )

    model.fit(X_train, y_train)

    print("Training complete!")

    # Create models directory
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save model
    joblib.dump(model, MODEL_PATH)

    # Save feature order
    with open(FEATURES_PATH, "w", encoding="utf-8") as file:
        for feature in X.columns:
            file.write(feature + "\n")

    print("\n=== MODEL SAVED ===")
    print(f"Model    : {MODEL_PATH}")
    print(f"Features : {FEATURES_PATH}")

    print("\nFeature order:")
    for i, feature in enumerate(X.columns, 1):
        print(f"{i:2}. {feature}")


if __name__ == "__main__":
    main()