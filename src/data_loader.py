import pandas as pd
from src.constants import CSV


# ! Hardcoded ! It's unclear why this list of columns is used.
def ld(p, yrs=None):
    keep = [
        "Start_Time", "Severity",
        "Weather_Condition", "Visibility(mi)", "Precipitation(in)",
        "Temperature(F)", "Wind_Speed(mph)",
        "Bump", "Crossing", "Street", "Description",
    ]
    df = pd.read_csv(p, usecols=lambda c: c in keep, on_bad_lines="skip")
    df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")
    df = df.dropna(subset=["Start_Time", "Severity"])
    if yrs:
        cut = df["Start_Time"].max() - pd.DateOffset(years=yrs)
        df = df[df["Start_Time"] >= cut]
    return df


def load_orifinal_data_csv():
    return pd.read_csv(CSV)