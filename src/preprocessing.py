import pandas as pd

def remove_outliers_iqr_entire_df(df):
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    return df


def remove_outliers_iqr_col(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    return df


def set_index_starting_from_one(df: pd.DataFrame) -> pd.DataFrame:
    df.index = range(1, len(df) + 1)
    return df


def object_columns_to_category(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    df_processed = df.copy()
    if columns is None:
        for col in df_processed.select_dtypes(include='object'):
            df_processed[col] = df_processed[col].str.lower().astype('category')
    else:
        for col in columns:
            df_processed[col] = df_processed[col].str.lower().astype('category')
    return df_processed
