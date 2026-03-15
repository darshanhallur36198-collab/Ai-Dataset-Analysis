import pandas as pd

def clean_dataset(df):
    df = df.drop_duplicates()

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            median_val = df[column].median()
            if not pd.isna(median_val):
                df[column] = df[column].fillna(median_val)
            else:
                df[column] = df[column].fillna(0)
        else:
            df[column] = df[column].fillna("Unknown")

    return df