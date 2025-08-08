import re
import numpy as np
import pandas as pd
from src.data_loader import load_orifinal_data_csv
import src.constants as consts
from src.visualization import plot_corr

# Functions
# def count_by_cities(df: pd.DataFrame, num_rows=consts.NUM_ROWS, cities=None) -> pd.DataFrame:
#     if cities is None:
#         df_processed = df['City'].value_counts().head(num_rows).reset_index()
#         df_processed.columns = ['City', 'Count']
#     else:
#         df_processed = df[df['City'].isin(cities)].groupby('City')['City'].count().head(num_rows).sort_values(by='City', ascending=False)
#         df_processed.columns = ['City', 'Count']
#     return df_processed

def count_by_cities(df: pd.DataFrame, num_rows=consts.NUM_ROWS, cities=None) -> pd.DataFrame:
    if cities is None:
        out = df['City'].value_counts().head(num_rows).reset_index()
        out.columns = ['City', 'Count']
        return out
    else:
        mask = df['City'].isin(cities)
        out = (
            df.loc[mask]
              .groupby('City', observed=True)
              .size()
              .reset_index(name='Count')
              .sort_values('Count', ascending=False)
              .head(num_rows)
        )
        return out

def feat(df):
    df = df.copy()

    if 'Start_Time' in df.columns and not np.issubdtype(df['Start_Time'].dtype, np.datetime64):
        df['Start_Time'] = pd.to_datetime(df['Start_Time'], errors='coerce')

    df["Severity"] = pd.to_numeric(df["Severity"], errors="coerce")
    df = df.dropna(subset=["Severity"])

    df["hour"] = df["Start_Time"].dt.hour
    df["day_of_week"] = df["Start_Time"].dt.dayofweek
    df["is_night"] = ((df["hour"] >= 20) | (df["hour"] <= 5)).astype(int)
    df["is_rush_hour"] = (df["hour"].between(7, 9) | df["hour"].between(16, 19)).astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["time_of_day"] = df["hour"].map(lambda h: "night" if h <= 5 else "morning" if h <= 9 else "day" if h <= 15 else "evening" if h <= 19 else "late")

    precipitation_column = next((c for c in df.columns if "Precipitation" in c), None)
    precipitation_values = pd.to_numeric(df[precipitation_column], errors="coerce").fillna(0) if precipitation_column else pd.Series(0, index=df.index, dtype="float64")
    df["has_precipitation"] = (precipitation_values > 0).astype(int)

    bad_weather_regex = r"Rain|Snow|Fog|Thunder|Storm|Hail|Sleet|Blizzard"
    weather_condition_series = df["Weather_Condition"] if "Weather_Condition" in df.columns else pd.Series("", index=df.index)
    df["has_bad_weather"] = weather_condition_series.fillna("").str.contains(bad_weather_regex, case=False, regex=True).astype(int)

    visibility_series = pd.to_numeric(df["Visibility(mi)"], errors="coerce") if "Visibility(mi)" in df.columns else pd.Series(np.nan, index=df.index)
    df["visibility_bin"] = pd.cut(visibility_series, [-np.inf, 2, 5, np.inf], labels=["<2", "2-5", ">5"])
    df["is_visibility_low"] = (df["visibility_bin"] == "<2").astype(int)

    temperature_column = next((c for c in df.columns if "Temp" in c), None)
    df["is_freezing"] = (pd.to_numeric(df[temperature_column], errors="coerce") < 32).astype(int) if temperature_column else 0

    wind_speed_column = next((c for c in df.columns if "Wind_Speed" in c), None)
    if wind_speed_column:
        df["wind_speed_bin"] = pd.cut(pd.to_numeric(df[wind_speed_column], errors="coerce"), [-.1, 7, 15, 25, np.inf], labels=["0", "1", "2", "3"])
    else:
        df["wind_speed_bin"] = pd.Categorical(["NA"] * len(df))

    df["road_type"] = (
        df["Street"]
          .fillna(df["Description"])
          .str.lower()
          .map(lambda text: (
              "interstate" if isinstance(text, str) and re.search(r"\b(i-|interstate|fwy)\b", text)
              else "highway" if isinstance(text, str) and re.search(r"\b(hwy|highway|us-|sr-)\b", text)
              else "local"
          ))
    )

    df["is_severe"] = (df["Severity"] >= 3).astype(int)
    bump_series = pd.to_numeric(df["Bump"], errors="coerce").fillna(0) if "Bump" in df.columns else pd.Series(0, index=df.index)
    crossing_series = pd.to_numeric(df["Crossing"], errors="coerce").fillna(0) if "Crossing" in df.columns else pd.Series(0, index=df.index)
    df["has_bump"] = bump_series.astype(int)
    df["has_crossing"] = crossing_series.astype(int)

    return df

def correlation_overview(df):

    for c in ["is_weekend", "time_of_day", "wind_speed_bin",
              "is_freezing", "road_type", "has_precipitation"]:
        show(df, c)

    num = [
        "Severity", "is_severe", "is_night", "is_rush_hour",
        "has_precipitation", "has_bad_weather", "is_visibility_low",
        "is_weekend", "is_freezing", "has_bump", "has_crossing",
    ]
    X = pd.get_dummies(df[["road_type", "wind_speed_bin", "time_of_day"]],
                       drop_first=True)
    data = pd.concat([df[num], X], axis=1).astype("float32", copy=False)

    corr = data.corr()
    plot_corr(corr)


def corr_show(df, feature_col):
    target_col = "is_severe"
    base = df[target_col].mean()
    g = (
        df.groupby(feature_col, observed=True)[target_col]
          .agg(count="size", share="mean")
          .reset_index()
    )
    g["count"] = g["count"].astype(int)
    g["delta_pct"] = (g["share"] / base - 1) * 100
    return g.sort_values("share", ascending=False), base

def show(df, feature_col):
    table, base = corr_show(df, feature_col)
    print(f"\n* {str(feature_col).upper()}  base={base:.3f}")
    for _, row in table.iterrows():
        print(
            f"{str(row[feature_col]):>10}  "
            f"count={int(row['count']):7d}  "
            f"share={row['share']:.3f}  "
            f"diff={row['delta_pct']:+6.1f}%"
        )
