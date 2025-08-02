import re
import numpy as np
import pandas as pd

def feat(df):
    df = df.copy()
    df["Severity"] = pd.to_numeric(df["Severity"], errors="coerce")
    df = df.dropna(subset=["Severity"])

    df["hr"]  = df["Start_Time"].dt.hour
    df["dow"] = df["Start_Time"].dt.dayofweek
    df["ngt"] = ((df["hr"] >= 20) | (df["hr"] <= 5)).astype(int)
    df["rush"] = (df["hr"].between(7, 9) | df["hr"].between(16, 19)).astype(int)
    df["wkd"] = (df["dow"] >= 5).astype(int)
    df["tod"] = df["hr"].map(
        lambda h: "n" if h <= 5 else "m" if h <= 9 else "d" if h <= 15 else "e" if h <= 19 else "l"
    )

    rain = pd.to_numeric(df.get("Precipitation(in)"), errors="coerce").fillna(0)
    df["prec"] = (rain > 0).astype(int)

    bad = r"Rain|Snow|Fog|Thunder|Storm|Hail|Sleet|Blizzard"
    df["bad"] = df.get("Weather_Condition", "").fillna("").str.contains(bad, case=False).astype(int)

    vis = pd.to_numeric(df.get("Visibility(mi)"), errors="coerce")
    df["vis"]  = pd.cut(vis, [-np.inf, 2, 5, np.inf], labels=["<2", "2-5", ">5"])
    df["vlow"] = (df["vis"] == "<2").astype(int)

    tcol = next((c for c in df.columns if "Temp" in c), None)
    df["frz"] = (pd.to_numeric(df[tcol], errors="coerce") < 32).astype(int) if tcol else 0

    wcol = next((c for c in df.columns if "Wind_Speed" in c), None)
    if wcol:
        df["wnd"] = pd.cut(
            pd.to_numeric(df[wcol], errors="coerce"),
            [-.1, 7, 15, 25, np.inf],
            labels=["0", "1", "2", "3"],
        )
    else:
        df["wnd"] = "NA"

    df["road"] = (
        df["Street"]
          .fillna(df["Description"])
          .str.lower()
          .map(
              lambda x: (
                  "int" if isinstance(x, str) and re.search(r"\b(i-|interstate|fwy)\b", x)
                  else "hwy" if isinstance(x, str) and re.search(r"\b(hwy|highway|us-|sr-)\b", x)
                  else "loc"
              )
          )
    )

    df["sev"]   = (df["Severity"] >= 3).astype(int)
    df["bump"]  = df.get("Bump", 0).fillna(0).astype(int)
    df["cross"] = df.get("Crossing", 0).fillna(0).astype(int)
    return df


def agg(df, col):
    base = df["sev"].mean()
    g = (
        df.groupby(col, observed=True)["sev"]
          .agg(["size", "mean"])
          .rename(columns={"size": "cnt", "mean": "share"})
          .reset_index()
    )
    g["cnt"] = g["cnt"].astype(int)
    g["d_pct"] = (g["share"] / base - 1) * 100
    return g.sort_values("share", ascending=False), base


def show(d, c):
    t, b = agg(d, c)
    print(f"\n* {c.upper()}  base={b:.3f}")
    for _, r in t.iterrows():
        print(
            f"{str(r[c]):>4}  cnt={int(r.cnt):7d}  share={r.share:.3f}  "
            f"diff={r.d_pct:+6.1f}%"
        )
