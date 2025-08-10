import re
import numpy as np
import pandas as pd
# from src.data_loader import load_orifinal_data_csv
import src.constants as consts
import src.preprocessing as prepro
import src.visualization as visualization
from src.preprocessing import object_columns_to_category


# Functions
# def count_by_cities_(df: pd.DataFrame, num_rows=consts.NUM_ROWS, cities=None) -> pd.DataFrame:
#     if cities is None:
#         out = df['City'].value_counts().head(num_rows).reset_index()
#         out.columns = ['City', 'NumOfAccidents']
#         return out
#     else:
#         mask = df['City'].isin(cities)
#         out = (
#             df.loc[mask]
#               .groupby('City', observed=True)
#               .size()
#               .reset_index(name='Count')
#               .sort_values('Count', ascending=False)
#               .head(num_rows)
#         )
#         return out
#


def correlation_overview(df):
    # 0) Пустой фрейм — выходим
    if df is None or df.empty:
        print('\n[Heatmap] No data after filtering. Load more rows or disable last-year drop.')
        return None

    # 1) Гарантируем, что фичи есть (если вдруг feat не вызывали)
    need = {
        "is_severe","is_weekend","is_night","is_rush_hour",
        "has_precipitation","has_bad_weather","is_visibility_low",
        "is_freezing","has_bump","has_crossing","road_type","wind_speed_bin",
    }
    if not need.issubset(df.columns):
        from src.analysis import feat
        df = feat(df)

    # 2) Печатаем лифты по нескольким ключевым признакам (один раз, без дублей)
    for c in ["is_weekend", "wind_speed_bin", "is_freezing", "road_type", "has_precipitation"]:
        if c in df.columns:
            show(df, c)
        else:
            print(f"(skip) {c} — column not found")

    # 3) Готовим матрицу для корреляции
    num = [
        "Severity", "is_severe", "is_night", "is_rush_hour",
        "has_precipitation", "has_bad_weather", "is_visibility_low",
        "is_weekend", "is_freezing", "has_bump", "has_crossing",
    ]
    use_num = [c for c in num if c in df.columns]

    # Категориальные — без time_of_day, как ты и хотел
    cat = [c for c in ["road_type", "wind_speed_bin"] if c in df.columns]
    if cat:
        X = pd.get_dummies(df[cat], drop_first=True, dtype="int8")
    else:
        X = pd.DataFrame(index=df.index)

    data = pd.concat([df[use_num].astype("float32", copy=False), X.astype("float32", copy=False)], axis=1)
    # drop constant columns (no variation) to avoid NaN stripes on heatmap
    nuniq = data.nunique(dropna=True)
    const_cols = nuniq[nuniq < 2].index.tolist()
    if const_cols:
        print("(skip) constant columns (no variation):", ", ".join(const_cols))
        data = data.drop(columns=const_cols, errors="ignore")

    if data.shape[1] == 0:
        print("(skip) all selected columns are constant")
        return

    if data.shape[1] == 0:
        print("(skip) nothing to correlate")
        return None

    corr = data.corr(numeric_only=True)
    visualization.plot_corr(corr)
    return corr


def count_by_cities(df: pd.DataFrame, num_rows=consts.NUM_ROWS, cities=None) -> pd.DataFrame:
    if cities is None:
        df_processed = df['City'].value_counts().head(num_rows).reset_index()
        df_processed.columns = ['City', 'NumOfAccidents']
    else:
        df_processed = df[df['City'].isin(cities)].groupby('City')['City'].count().head(num_rows).sort_values(by='City', ascending=False)
        df_processed.columns = ['City', 'NumOfAccidents']
    prepro.set_index_starting_from_one(df_processed)
    return df_processed


def feat(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["Start_Time"] = pd.to_datetime(d["Start_Time"], errors="coerce")
    d["Severity"] = pd.to_numeric(d["Severity"], errors="coerce")
    d = d.dropna(subset=["Start_Time","Severity"])

    d["hour"] = d["Start_Time"].dt.hour
    d["day_of_week"] = d["Start_Time"].dt.dayofweek
    d["is_night"] = ((d["hour"] >= 20) | (d["hour"] <= 5)).astype(int)
    d["is_rush_hour"] = (d["hour"].between(7,9) | d["hour"].between(16,19)).astype(int)
    d["is_weekend"] = (d["day_of_week"] >= 5).astype(int)

    pcol = next((c for c in d.columns if "Precipitation" in c), None)
    d["has_precipitation"] = (pd.to_numeric(d[pcol], errors="coerce").fillna(0) > 0).astype(int) if pcol else 0

    bad_re = r"Rain|Snow|Fog|Thunder|Storm|Hail|Sleet|Blizzard"

    if "Weather_Condition" in d.columns:
        w = d["Weather_Condition"].astype("string").fillna("")
    else:
        w = pd.Series("", index=d.index, dtype="string")

    d["has_bad_weather"] = w.str.contains(bad_re, case=False, regex=True) \
        .fillna(False).astype(int)

    v = pd.to_numeric(d["Visibility(mi)"], errors="coerce") if "Visibility(mi)" in d.columns else pd.Series(np.nan, index=d.index)
    d["is_visibility_low"] = (v < 2).astype(int)

    tcol = next((c for c in d.columns if "Temp" in c), None)
    d["is_freezing"] = (pd.to_numeric(d[tcol], errors="coerce") < 32).astype(int) if tcol else 0


    wcol = next((c for c in d.columns if "Wind_Speed" in c), None)
    if wcol:
        d["wind_speed_bin"] = pd.cut(pd.to_numeric(d[wcol], errors="coerce"), [-.1, 7, 15, 25, np.inf], labels=["0","1","2","3"])
    else:
        d["wind_speed_bin"] = pd.Categorical(["NA"] * len(d))

    txt = d["Street"].fillna(d.get("Description")).astype(str).str.lower()
    d["road_type"] = txt.map(lambda s:
        "interstate" if re.search(r"\b(i-|interstate|fwy)\b", s) else
        ("highway" if re.search(r"\b(hwy|highway|us-|sr-)\b", s) else "local")
    )

    d["is_severe"] = (d["Severity"] >= 3).astype(int)
    if "Bump" in d.columns:
        d["has_bump"] = d["Bump"].astype(str).str.lower().isin(["true", "1", "yes"]).astype(int)
    else:
        d["has_bump"] = 0
    if "Crossing" in d.columns:
        d["has_crossing"] = d["Crossing"].astype(str).str.lower().isin(["true", "1", "yes"]).astype(int)
    else:
        d["has_crossing"] = 0

    d = object_columns_to_category(d, columns=["City", "Weather_Condition", "road_type"])
    return d


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

def count_by_cities_years(df: pd.DataFrame, num_rows=consts.NUM_ROWS, cities=None, year=2023) -> pd.DataFrame:
    if cities is None:
        df_processed = pd.DataFrame({
            "City": df['City'],
            'Year': pd.to_datetime(df['Start_Time']).dt.year
        })
        df_processed = df_processed[df_processed['Year'] == year]['City']
        df_processed = df_processed.value_counts().head(num_rows).reset_index()
        df_processed.columns = ['City', 'NumOfAccidents']
    else:
        df_processed = df[df['City'].isin(cities)].groupby('City')['City'].count().head(num_rows).sort_values(by='City', ascending=False)
        df_processed.columns = ['City', 'NumAccidents']
    prepro.set_index_starting_from_one(df_processed)
    return df_processed


def city_accidents_count_by_year(df: pd.DataFrame, num_rows=consts.NUM_ROWS, city='new york') -> pd.DataFrame:
    df_processed = pd.DataFrame({
        "City": df['City'],
        'Year': pd.to_datetime(df['Start_Time']).dt.year
    })
    df_processed = df_processed[df['City'] == city]
    df_processed = df_processed.groupby('Year')['City'].count().reset_index()
    # df_processed.columns = ['City', 'Year', 'NumAccidents']
    prepro.set_index_starting_from_one(df_processed)
    return df_processed
