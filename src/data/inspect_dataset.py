import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/raw/PhiUSIIL_Phishing_URL_Dataset.csv")


def main():
    print("Loading dataset...")
    
    df = pd.read_csv(DATA_PATH)

    print("\n=== DATASET OVERVIEW ===")
    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]}")

    print("\n=== COLUMNS ===")
    for i, column in enumerate(df.columns, 1):
        print(f"{i:2}. {column}")

    print("\n=== FIRST 5 ROWS ===")
    print(df.head())

    print("\n=== DATA TYPES ===")
    print(df.dtypes)

    print("\n=== MISSING VALUES ===")
    missing = df.isnull().sum()
    print(missing[missing > 0])

    print("\n=== LABEL DISTRIBUTION ===")
    if "label" in df.columns:
        print(df["label"].value_counts())
    else:
        print("'label' column not found.")


if __name__ == "__main__":
    main()