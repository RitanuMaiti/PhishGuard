import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split


DATA_PATH = "data/processed/url_features.csv"
MODEL_PATH = "models/phishguard_model.joblib"


def main():

    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    feature_names = [
        column
        for column in df.columns
        if column != "label"
    ]

    X = df[feature_names]
    y = df["label"]

    # ---------------------------------------------------------
    # IMPORTANT:
    # Split URLs BEFORE removing duplicates.
    #
    # This evaluates performance on URLs that the model
    # did not see during training.
    # ---------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"Total URLs : {len(df):,}")
    print(f"Training   : {len(X_train):,}")
    print(f"Test       : {len(X_test):,}")

    # ---------------------------------------------------------
    # Load final model
    # ---------------------------------------------------------

    print("\nLoading trained model...")

    model = joblib.load(MODEL_PATH)

    # ---------------------------------------------------------
    # Predictions
    # ---------------------------------------------------------

    print("Running predictions...")

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    # ---------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
    )

    recall = recall_score(
        y_test,
        predictions,
    )

    f1 = f1_score(
        y_test,
        predictions,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print("\n" + "=" * 55)
    print("PHISHGUARD GENERALIZATION TEST")
    print("=" * 55)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1       : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    # ---------------------------------------------------------
    # Confusion matrix
    # ---------------------------------------------------------

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    print("\nConfusion Matrix")
    print("----------------")
    print(matrix)

    # ---------------------------------------------------------
    # Detailed classification report
    # ---------------------------------------------------------

    print("\nClassification Report")
    print("---------------------")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "LEGITIMATE",
                "PHISHING",
            ],
        )
    )

    # ---------------------------------------------------------
    # Error analysis
    # ---------------------------------------------------------

    test_results = X_test.copy()

    test_results["actual"] = y_test.values
    test_results["predicted"] = predictions
    test_results["probability"] = probabilities

    errors = test_results[
        test_results["actual"]
        != test_results["predicted"]
    ]

    print(
        f"\nMisclassified URLs: "
        f"{len(errors):,}"
    )

    print("\nSample errors:")

    print(
        errors[
            [
                "url_length",
                "domain_length",
                "has_https",
                "domain_entropy",
                "has_login",
                "actual",
                "predicted",
                "probability",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()