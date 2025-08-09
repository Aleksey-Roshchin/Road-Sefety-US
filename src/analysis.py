import re
import numpy as np
import pandas as pd
# from src.data_loader import load_orifinal_data_csv
import src.constants as consts
from src.visualization import plot_corr

from src.visualization import plot_corr

def correlation_overview(df):

    if df is None or df.empty:
        print('\n[Heatmap] No data after filtering (maybe last year drop on a small sample). Try loading more rows or disable last-year drop for sample load.')
        return

    for c in ["is_weekend", "time_of_day", "wind_speed_bin", "is_freezing", "road_type", "has_precipitation"]:
        show(df, c)
        show(df, c)

    num = [
        "Severity", "is_severe", "is_night", "is_rush_hour",
        "has_precipitation", "has_bad_weather", "is_visibility_low",
        "is_weekend", "is_freezing", "has_bump", "has_crossing",
    ]

    X = pd.get_dummies(df[["road_type", "wind_speed_bin", "time_of_day"]], drop_first=True)
    data = pd.concat([df[num], X], axis=1).astype("float32", copy=False)
    corr = data.corr()
    plot_corr(corr)

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

def _year_col(df):
    return pd.to_datetime(df['Start_Time'], errors='coerce').dt.year

def kpi_by_year(df: pd.DataFrame, metric: str = 'accidents') -> pd.DataFrame:
    y = pd.to_datetime(df['Start_Time'], errors='coerce').dt.year
    g = df.copy().assign(year=y)

    if metric == 'accidents':
        out = g.groupby('year').size().reset_index(name='accidents')
    elif metric == 'severe_share':
        out = g.groupby('year')['is_severe'].mean().reset_index(name='severe_share')
    elif metric == 'avg_severity':
        out = g.groupby('year')['Severity'].mean().reset_index(name='avg_severity')
    elif metric == 'weekend_share':
        out = g.groupby('year')['is_weekend'].mean().reset_index(name='weekend_share')
    elif metric == 'precip_share':
        out = g.groupby('year')['has_precipitation'].mean().reset_index(name='precip_share')
    elif metric == 'bad_weather_share':
        out = g.groupby('year')['has_bad_weather'].mean().reset_index(name='bad_weather_share')
    else:
        out = g.groupby('year').size().reset_index(name='accidents')

    out = out.dropna()
    if 'year' in out.columns:
        out['year'] = out['year'].astype(int)

    value_col = [c for c in out.columns if c != 'year'][0]
    if value_col.endswith('_share'):
        out[value_col] = (out[value_col] * 100).round(1)  # percent
    elif value_col == 'avg_severity':
        out[value_col] = out[value_col].round(2)

    return out.sort_values('year')


def kpi_by_year_all(df: pd.DataFrame) -> pd.DataFrame:

    y = pd.to_datetime(df['Start_Time'], errors='coerce').dt.year
    g = df.copy().assign(year=y)

    out = (
        g.groupby('year')
         .agg(
             accidents=('Severity', 'size'),
             severe_share=('is_severe', 'mean'),
             avg_severity=('Severity', 'mean'),
             weekend_share=('is_weekend', 'mean'),
             precip_share=('has_precipitation', 'mean'),
             bad_weather_share=('has_bad_weather', 'mean'),
         )
         .reset_index()
    )

    out['year'] = out['year'].astype(int)
    for c in ['severe_share', 'weekend_share', 'precip_share', 'bad_weather_share']:
        out[c] = (out[c] * 100).round(1)
    out['avg_severity'] = out['avg_severity'].round(2)
    return out.sort_values('year')

def kpi_components_by_year(df: pd.DataFrame, scale: int = 10000) -> pd.DataFrame:

    g = df.copy()
    g["year"] = pd.to_datetime(g["Start_Time"], errors="coerce").dt.year

    severe = g.get("is_severe", pd.Series(0, index=g.index)).astype(bool)
    weekend = g.get("is_weekend", pd.Series(0, index=g.index)).astype(bool)
    precip = g.get("has_precipitation", pd.Series(0, index=g.index)).astype(bool)
    bad    = g.get("has_bad_weather", pd.Series(0, index=g.index)).astype(bool)

    bucket_severe = severe
    bucket_weekend = (~bucket_severe) & weekend
    bucket_precip = (~bucket_severe) & (~bucket_weekend) & precip
    bucket_bad    = (~bucket_severe) & (~bucket_weekend) & (~bucket_precip) & bad
    bucket_other  = ~(bucket_severe | bucket_weekend | bucket_precip | bucket_bad)

    parts = pd.DataFrame({
        "year": g["year"],
        "severe": bucket_severe.astype(int),
        "weekend_only": bucket_weekend.astype(int),
        "precip_only": bucket_precip.astype(int),
        "bad_only": bucket_bad.astype(int),
        "other": bucket_other.astype(int),
    })

    agg = parts.groupby("year", as_index=False).sum()

    totals = g.groupby("year", as_index=False).size().rename(columns={"size": "accidents"})

    out = agg.merge(totals, on="year", how="left")

    for c in ["severe", "weekend_only", "precip_only", "bad_only", "other", "accidents"]:
        out[c] = (out[c] / float(scale)).round(2)

    return out.sort_values("year")
