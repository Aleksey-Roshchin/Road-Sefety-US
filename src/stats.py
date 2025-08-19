# src/stats.py
import pandas as pd

def chi2_bulk_severe_vs_common_factors(df: pd.DataFrame, alpha: float = 0.05) -> None:
    """Runs chi-square: is_severe × each common factor (no prompts)."""
    import src.analysis as analysis
    d = analysis.ensure_features(df)

    factors = [
        "is_weekend", "is_night", "is_rush_hour",
        "has_precipitation", "has_bad_weather",
        "is_visibility_low", "is_freezing",
        "has_bump", "has_crossing",
        "wind_speed_bin", "road_type",
    ]

    # try to use SciPy; if not available — fallback to percents
    try:
        from scipy.stats import chi2_contingency
        have_scipy = True
    except Exception:
        have_scipy = False
        print("Tip: to see p-values, install once:  pip install scipy")

    for f in factors:
        print(f"\n=== is_severe × {f} ===")
        if f not in d.columns:
            print("(skip) column not found")
            continue

        ct = pd.crosstab(d["is_severe"], d[f], dropna=False)

        # 1) выбросить пустые строки/столбцы (сумма = 0)
        ct = ct.loc[ct.sum(axis=1) > 0, ct.sum(axis=0) > 0]

        print("Observed counts:\n", ct)

        # 2) если после чистки нет как минимум 2x2 — показать проценты и дальше
        if ct.shape[0] < 2 or ct.shape[1] < 2 or not have_scipy:
            perc = (ct.T / ct.T.sum()).T.fillna(0) * 100
            print("Row-wise percentages (%):\n", perc.round(2))
            continue

        # 3) χ² (Yates для 2x2)
        use_yates = (ct.shape == (2, 2))
        chi2, p, dof, _ = chi2_contingency(ct.values, correction=use_yates)
        v = _cramers_v(chi2, ct)
        p_str = f"{p:.6f}" if p >= 1e-6 else "< 1e-6"
        print(f"chi2={chi2:.3f}, dof={dof}, p-value={p_str}  (Yates={use_yates})")
        print(f"Cramer's V={v:.3f}")
        print("Result:", "REJECT H0 (dependence)" if p <= 0.05 else "Fail to reject H0 (no evidence)")

        print(f"chi2={chi2:.3f}, dof={dof}, p-value={p:.6f}  (Yates={use_yates})")
        print("Result:", "REJECT H0 (dependence)" if p <= alpha else "Fail to reject H0 (no evidence)")

def _cramers_v(chi2, ct):
    n = ct.values.sum()
    r, c = ct.shape
    k = min(r, c) - 1
    if n == 0 or k <= 0:
        return float("nan")
    return (chi2 / (n * k)) ** 0.5

def _add_dui_flag(d: pd.DataFrame) -> pd.DataFrame:
    """Heuristic flag from Description: 'dui', 'dwi', 'drunk', 'intoxicated', 'alcohol', 'sobriety checkpoint', 'impaired'."""
    if "Description" not in d.columns:
        d["has_dui_signal"] = 0
        return d
    # в src/stats.py внутри _add_dui_flag(...)
    desc = d["Description"].astype(str).str.lower()
    pat = r"(?:dui|dwi|drunk|intoxicat(?:ed|ion)|impaired|alcohol|sobriety\s+checkpoint)"
    d["has_dui_signal"] = desc.str.contains(pat, regex=True, na=False).astype(int)

    return d

def _safe_crosstab(df, x, y):
    ct = pd.crosstab(df[x], df[y], dropna=False)
    # drop empty rows/cols (sum==0) to avoid SciPy zero-expected error
    ct = ct.loc[ct.sum(axis=1) > 0, ct.sum(axis=0) > 0]
    return ct

# --- main entrypoint ---

def global_influence_scan(df: pd.DataFrame, alpha: float = 0.05) -> None:
    """
    One-button scan: ranks factors by strength of association with is_severe.
    Prints summary table + severe rates per factor.
    """
    # 1) ensure engineered features
    import src.analysis as analysis
    d = analysis.ensure_features(df).copy()
    d = _add_dui_flag(d)

    # 2) candidate factors (из твоих KPI/feature-блока)
    factors = [
        "road_type",
        "has_crossing",
        "wind_speed_bin",
        "has_precipitation",
        "has_bad_weather",
        "is_night",
        "is_weekend",
        "is_rush_hour",
        "is_freezing",
        "is_visibility_low",
        "has_bump",
        "has_dui_signal",  # эвристика из Description
    ]

    # 3) SciPy (для p-value) — если нет, просто печатаем проценты и V не считаем
    try:
        from scipy.stats import chi2_contingency
        have_scipy = True
    except Exception:
        have_scipy = False
        print("Tip: to see p-values/Cramer's V, install once:  pip install scipy")

    rows = []
    for f in factors:
        if f not in d.columns:
            continue
        ct = _safe_crosstab(d, "is_severe", f)
        if ct.shape[0] < 2 or ct.shape[1] < 2:
            # not enough variation
            rates = (d.groupby(f)["is_severe"].mean() * 100).sort_values(ascending=False)
            rows.append({"factor": f, "k": ct.shape[1], "delta_pp": float((rates.max() - rates.min()) if len(rates) else 0.0),
                         "cramers_v": float("nan"), "p_value": "n/a", "note": "one category only"})
            continue

        # rates spread
        rates = (d.groupby(f, observed=True)["is_severe"].mean() * 100)
        delta_pp = float((rates.max() - rates.min()))

        if have_scipy:
            use_yates = (ct.shape == (2, 2))
            chi2, p, dof, _ = chi2_contingency(ct.values, correction=use_yates)
            v = _cramers_v(chi2, ct)
            p_str = f"{p:.6f}" if p >= 1e-6 else "< 1e-6"
            rows.append({
                "factor": f, "k": ct.shape[1], "delta_pp": round(delta_pp, 2),
                "cramers_v": round(v, 3), "p_value": p_str, "note": ""
            })
        else:
            rows.append({
                "factor": f, "k": ct.shape[1], "delta_pp": round(delta_pp, 2),
                "cramers_v": float("nan"), "p_value": "install scipy", "note": ""
            })

    if not rows:
        print("No factors to scan.")
        return

    out = pd.DataFrame(rows).sort_values(
        by=["cramers_v", "delta_pp"], ascending=[False, False], na_position="last"
    )

    print("\n=== Global influence scan (target: is_severe) ===")
    print(out.to_string(index=False))

    # show per-factor severe rates for top-3 by V (если есть V) или по delta_pp
    top = out.dropna(subset=["cramers_v"]).head(3)
    if top.empty:
        top = out.head(3)
    for f in top["factor"]:
        rates = (d.groupby(f)["is_severe"].mean() * 100).sort_values(ascending=False).round(2)
        print(f"\nSevere share by '{f}' (%):")
        print(rates.to_string())