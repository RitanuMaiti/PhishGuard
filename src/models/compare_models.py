import time

import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


DATA_PATH = "data/processed/url_features.csv"


def main():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    # Remove duplicate feature patterns
    df = df.drop_duplicates()

    X = df.drop(columns=["label"])
    y = df["label"]

    print(f"Unique feature rows: {len(df):,}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",
        ),

        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            )),
        ]),

        "Hist Gradient Boosting": HistGradientBoostingClassifier(
            max_iter=200,
            learning_rate=0.1,
            random_state=42,
        ),
    }

    results = []

    for name, model in models.items():
        print(f"\n{'=' * 50}")
        print(f"Training: {name}")
        print("=" * 50)

        start = time.perf_counter()

        model.fit(X_train, y_train)

        training_time = time.perf_counter() - start

        start = time.perf_counter()

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        inference_time = time.perf_counter() - start

        results.append({
            "Model": name,
            "Accuracy": accuracy_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred),
            "Recall": recall_score(y_test, y_pred),
            "F1": f1_score(y_test, y_pred),
            "ROC-AUC": roc_auc_score(y_test, y_prob),
            "PR-AUC": average_precision_score(y_test, y_prob),
            "Training Time (s)": training_time,
            "Inference Time (s)": inference_time,
        })

        print(f"Accuracy : {results[-1]['Accuracy']:.4f}")
        print(f"Precision: {results[-1]['Precision']:.4f}")
        print(f"Recall   : {results[-1]['Recall']:.4f}")
        print(f"F1       : {results[-1]['F1']:.4f}")
        print(f"ROC-AUC  : {results[-1]['ROC-AUC']:.4f}")
        print(f"PR-AUC   : {results[-1]['PR-AUC']:.4f}")

    results_df = pd.DataFrame(results)

    print("\n\n=== MODEL COMPARISON ===")
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()