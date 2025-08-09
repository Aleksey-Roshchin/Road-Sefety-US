import pandas as pd

def parse_dates(df: pd.DataFrame, col: str = 'Start_Time') -> pd.DataFrame:
    if col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors='coerce')
    df = df.dropna(subset=[col])
    df['year'] = df[col].dt.year
    df['date'] = df[col].dt.date
    return df

def remove_outliers_basic(df, cols=None):
    if cols is None:
        return remove_outliers_iqr_entire_df(df)
    for c in cols:
        if c in df.columns:
            df = remove_outliers_iqr_col(df, c)
    return df


def drop_incomplete_last_year(df: pd.DataFrame, col: str = 'Start_Time') -> pd.DataFrame:
    y = pd.to_datetime(df[col], errors='coerce').dt.year
    last_year = y.max()
    if pd.notna(last_year):
        df = df[y < last_year]
    return df

def base_preprocess_datetime(
    df: pd.DataFrame,
    col: str = 'Start_Time',
    drop_last_year: bool = True,
    apply_outliers: bool = False,
    outlier_cols=None
) -> pd.DataFrame:
    df = parse_dates(df, col)
    if drop_last_year:
        df = drop_incomplete_last_year(df, col)
    if apply_outliers:
        df = remove_outliers_basic(df, cols=outlier_cols)
    return df


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