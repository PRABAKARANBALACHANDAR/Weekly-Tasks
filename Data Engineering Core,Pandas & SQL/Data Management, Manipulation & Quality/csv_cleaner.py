import pandas as pd
import numpy as np
from pathlib import Path

def clean_column_names(df):
    df.columns=(df.columns.str.strip().str.lower().str.replace(" ", "_"))
    return df

def strip_whitespace(df):
    for col in df.select_dtypes(include="object").columns:
        df[col]=df[col].astype(str).str.strip()
    return df

def convert_numeric(df):
    for col in df.columns:
        df[col]=pd.to_numeric(df[col], errors="ignore")
    return df

def convert_binary_columns(df):
    for col in df.columns:
        unique_values=df[col].dropna().unique()

        if len(unique_values)==2:
            sorted_vals=sorted(unique_values)
            mapping={sorted_vals[0]: 0, sorted_vals[1]: 1}
            df[col]=df[col].map(mapping)
    return df

def handle_missing_values(df):
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            df[col]=df[col].fillna(df[col].median())
        else:
            df[col]=df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "unknown")
    return df

def remove_outliers(df, z_threshold=3):
    numeric_cols=df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        mean=df[col].mean()
        std=df[col].std()
        if std != 0:
            z_scores=(df[col] - mean) / std
            df=df[np.abs(z_scores) < z_threshold]
    return df

def clean_csv(input_file, output_file, filter_column=None, filter_value=None, sort_column=None, rename_map=None, remove_outlier_rows=False):
    try:
        input_path=Path(input_file)

        if not input_path.exists():
            print("file not found")
            return

        df=pd.read_csv(input_path)

    except pd.errors.EmptyDataError:
        print("csv file is empty")
        return

    except pd.errors.ParserError:
        print("error parsing csv")
        return

    except Exception as e:
        print("error reading file:", e)
        return

    try:
        df=clean_column_names(df)
        df=strip_whitespace(df)
        df=df.drop_duplicates()
        df=df.replace("", np.nan)

        df=convert_numeric(df)
        df=convert_binary_columns(df)
        df=handle_missing_values(df)

        if rename_map:
            df=df.rename(columns=rename_map)

        if filter_column and filter_value is not None:
            if filter_column in df.columns:
                df=df[df[filter_column]==filter_value]

        if sort_column:
            if sort_column in df.columns:
                df=df.sort_values(sort_column)

        if remove_outlier_rows:
            df=remove_outliers(df)

        df.to_csv(output_file, index=False)

        print("cleaning completed successfully")
        print("final rows:", len(df))
        print("final columns:", len(df.columns))

    except Exception as e:
        print("error during cleaning:", e)

if __name__=="__main__":
    clean_csv(input_file="automobile_dataset.csv", output_file="cleaned.csv")