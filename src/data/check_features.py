import pandas as pd

DATA_PATH = "data/processed/url_features.csv"


def main():
    print("Loading processed features...")
    df = pd.read_csv(DATA_PATH)

    print("\n=== SHAPE ===")
    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]}")

    print("\n=== DATA TYPES ===")
    print(df.dtypes)

    print("\n=== MISSING VALUES ===")
    missing = df.isnull().sum()
    print(missing[missing > 0])

    print("\n=== LABEL DISTRIBUTION ===")
    print(df["label"].value_counts())
    print("\nLabel percentages:")
    print((df["label"].value_counts(normalize=True) * 100).round(2))

    print("\n=== FEATURE RANGES ===")

    feature_columns = df.drop(columns=["label"]).columns

    for column in feature_columns:
        print(
            f"{column:25} "
            f"min={df[column].min():.4f}  "
            f"max={df[column].max():.4f}"
        )

    print("\n=== DUPLICATE ROWS ===")
    print(f"Duplicate rows: {df.duplicated().sum():,}")

    print("\n=== CORRELATION WITH LABEL ===")
    correlations = (
        df.corr(numeric_only=True)["label"]
        .drop("label")
        .sort_values(key=abs, ascending=False)
    )

    print(correlations)


if __name__ == "__main__":
    main()