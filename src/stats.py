# src/stats.py
import pandas as pd

def chi2_bulk_severe_vs_common_factors(df: pd.DataFrame, alpha: float = 0.05) -> None:
    """Chi-square test: is_severe vs. each common factor."""
    import src.analysis as analysis
    d = analysis.ensure_features(df)

    factors = [
        "is_weekend", "is_night", "is_rush_hour",
        "has_precipitation", "has_bad_weather",
        "is_visibility_low", "is_freezing",
        "has_bump", "has_crossing",
        "wind_speed_bin", "road_type",
    ]

    try:
        from scipy.stats import chi2_contingency
        have_scipy = True
    except Exception:
        have_scipy = False
        print("Tip: install scipy to see p-values")

    for f in factors:
        print(f"\n=== is_severe × {f} ===")
        if f not in d.columns:
            print("column not found")
            continue

        ct = pd.crosstab(d["is_severe"], d[f])
        print("Counts:\n", ct)

        if not have_scipy or ct.shape[0] < 2 or ct.shape[1] < 2:
            continue

        use_yates = ct.shape == (2, 2)
        chi2, p, dof, _ = chi2_contingency(ct.values, correction=use_yates)
        v = _cramers_v(chi2, ct)
        result = "REJECT H0 (dependence)" if p <= alpha else "Fail to reject H0 (no evidence)"
        print(f"chi2={chi2:.3f}, dof={dof}, p={p:.6f}, V={v:.3f} (Yates={use_yates})")
        print("Result:", result)

def _cramers_v(chi2, ct):
    n = ct.values.sum()
    r, c = ct.shape
    k = min(r, c) - 1
    if n == 0 or k <= 0:
        return float("nan")
    return (chi2 / (n * k)) ** 0.5
