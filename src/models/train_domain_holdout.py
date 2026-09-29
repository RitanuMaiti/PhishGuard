import joblib
import pandas as pd
import tldextract

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.model_selection import GroupShuffleSplit


DATA_PATH = "data/processed/url_features.csv"
RAW_PATH = "data/raw/PhiUSIIL_Phishing_URL_Dataset.csv"


def get_registered_domain(url):
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
    # Group every URL by registered domain
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
    # Domain-level train/test split
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
        f"\nTraining URLs   : {len(X_train):,}"
    )

    print(
        f"Test URLs       : {len(X_test):,}"
    )

    print(
        f"Training domains: {len(train_domains):,}"
    )

    print(
        f"Test domains    : {len(test_domains):,}"
    )

    print(
        f"Domain overlap  : {len(overlap)}"
    )

    if overlap:
        raise RuntimeError(
            "Domain leakage detected!"
        )

    print(
        "\n✓ Zero domain overlap."
    )

    # ---------------------------------------------------------
    # Train ONLY on training domains
    # ---------------------------------------------------------

    print(
        "\nTraining Hist Gradient Boosting..."
    )

    model = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.1,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    print("Training complete.")

    # ---------------------------------------------------------
    # Evaluate ONLY on unseen domains
    # ---------------------------------------------------------

    print(
        "\nEvaluating on unseen domains..."
    )

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

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
        "CLEAN UNSEEN-DOMAIN EVALUATION"
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

    print("\nConfusion Matrix")
    print("----------------")

    print(
        confusion_matrix(
            y_test,
            predictions,
        )
    )

    # ---------------------------------------------------------
    # Save temporary evaluation model
    # ---------------------------------------------------------

    output_path = (
        "models/"
        "phishguard_domain_holdout.joblib"
    )

    joblib.dump(
        model,
        output_path,
    )

    print(
        f"\nEvaluation model saved:"
        f"\n{output_path}"
    )


if __name__ == "__main__":
    main()