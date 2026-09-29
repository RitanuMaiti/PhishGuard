import pandas as pd
from pathlib import Path

from src.features.url_features import extract_features


INPUT_PATH = Path("data/raw/PhiUSIIL_Phishing_URL_Dataset.csv")
OUTPUT_PATH = Path("data/processed/url_features.csv")


def main():
    print("Loading dataset...")

    df = pd.read_csv(INPUT_PATH)

    print(f"Loaded {len(df):,} URLs")

    print("Extracting features...")

    feature_rows = []

    for url in df["URL"]:
        feature_rows.append(extract_features(url))

    features_df = pd.DataFrame(feature_rows)

    features_df["label"] = df["label"].map({
        0: 1,  # phishing
        1: 0,  # legitimate
    })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    features_df.to_csv(OUTPUT_PATH, index=False)

    print("\nFeature extraction complete!")
    print(f"Rows    : {len(features_df):,}")
    print(f"Columns : {len(features_df.columns)}")
    print(f"Saved   : {OUTPUT_PATH}")

    print("\nLabel distribution:")
    print(features_df["label"].value_counts())

    print("\nFirst 5 rows:")
    print(features_df.head())


if __name__ == "__main__":
    main()