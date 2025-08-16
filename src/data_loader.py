import pandas as pd
from src.constants import CSV
from src.preprocessing import object_columns_to_category

# ! Hardcoded ! It's unclear why this list of columns is used.
from src.preprocessing import base_preprocess_datetime

def load_original_data_csv():
    return pd.read_csv(CSV)

def ld(p, yrs=None):
    keep = [
        "Start_Time", "Severity",
        "City",
        "Weather_Condition", "Visibility(mi)", "Precipitation(in)",
        "Temperature(F)", "Wind_Speed(mph)",
        "Bump", "Crossing", "Street", "Description",
    ]
    df = pd.read_csv(p, usecols=lambda c: c in keep, on_bad_lines="skip")
    df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")
    df = df.dropna(subset=["Start_Time", "Severity"])
    df = base_preprocess_datetime(
        df,
        apply_outliers=True,
        outlier_cols=["Visibility(mi)", "Precipitation(in)", "Temperature(F)", "Wind_Speed(mph)"]
    )
    df = df[df["year"].between(2016, 2023)]
    df = df.dropna(subset=["City"])
    df = object_columns_to_category(df, columns=["City", "Weather_Condition"])
    return df
