import joblib
import pandas as pd
import tldextract

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import GroupShuffleSplit


DATA_PATH = "data/processed/url_features.csv"
RAW_PATH = "data/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
MODEL_PATH = "models/phishguard_model.joblib"


def get_registered_domain(url):
    """Extract registered domain used for grouping."""

    extracted = tldextract.extract(url)

    return extracted.top_domain_under_public_suffix


def main():

    print("Loading datasets...")

    features_df = pd.read_csv(DATA_PATH)
    raw_df = pd.read_csv(RAW_PATH)

    feature_names = [
        column
        for column in features_df.columns
        if column != "label"
    ]

    X = features_df[feature_names]
    y = features_df["label"]

    # ---------------------------------------------------------
    # Create registered-domain groups
    # ---------------------------------------------------------

    print("Extracting registered domains...")

    groups = raw_df["URL"].apply(
        get_registered_domain
    )

    print(
        f"Unique registered domains: "
        f"{groups.nunique():,}"
    )

    # ---------------------------------------------------------
    # Split by registered domain
    #
    # URLs belonging to the same registered domain
    # cannot appear in both train and test.
    # ---------------------------------------------------------

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42,
    )

    train_idx, test_idx = next(
        splitter.split(
            X,
            y,
            groups=groups,
        )
    )

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    train_domains = set(
        groups.iloc[train_idx]
    )

    test_domains = set(
        groups.iloc[test_idx]
    )

    overlap = train_domains & test_domains

    print(
        f"\nTraining URLs : {len(X_train):,}"
    )

    print(
        f"Test URLs     : {len(X_test):,}"
    )

    print(
        f"Training domains: "
        f"{len(train_domains):,}"
    )

    print(
        f"Test domains    : "
        f"{len(test_domains):,}"
    )

    print(
        f"Domain overlap : "
        f"{len(overlap)}"
    )

    # ---------------------------------------------------------
    # Verify that there is ZERO domain leakage
    # ---------------------------------------------------------

    if overlap:
        raise RuntimeError(
            "Domain leakage detected!"
        )

    print(
        "\n✓ No registered-domain overlap "
        "between train and test."
    )

    # ---------------------------------------------------------
    # Load trained model
    # ---------------------------------------------------------

    print("\nLoading trained model...")

    model = joblib.load(MODEL_PATH)

    # ---------------------------------------------------------
    # Predictions
    # ---------------------------------------------------------

    print("Running predictions...")

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

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

    print("\n" + "=" * 60)
    print(
        "PHISHGUARD UNSEEN-DOMAIN GENERALIZATION TEST"
    )
    print("=" * 60)

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1       : {f1:.4f}"
    )

    print(
        f"ROC-AUC  : {roc_auc:.4f}"
    )

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
    # Classification report
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


if __name__ == "__main__":
    main()