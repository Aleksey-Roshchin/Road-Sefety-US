import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_corr(corr: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 9), dpi=200)
    plt.imshow(corr, vmin=-1, vmax=1)
    plt.xticks(range(len(corr)), corr.columns, rotation=90, fontsize=6)
    plt.yticks(range(len(corr)), corr.index, fontsize=6)
    plt.colorbar()
    plt.tight_layout()
    plt.show()


def bar_plot(df: pd.DataFrame, x_col: str, y_col: str, filename: str = 'temp/barplot.png') -> None:
    plt.figure(figsize=(12, 9))
    sns.barplot(data=df, x=x_col, y=y_col)
    plt.show()


def multi_bar_plot(df, x_col, y_cols, title="KPIs by year"):
    data = df.copy()
    x = data[x_col].astype(str).tolist()
    n = len(y_cols)
    idx = np.arange(len(x))
    total_width = 0.8
    width = total_width / max(n, 1)
    fig, ax = plt.subplots()
    for i, col in enumerate(y_cols):
        y = pd.to_numeric(data[col], errors="coerce").fillna(0.0).values
        offset = (i - (n - 1) / 2) * width
        ax.bar(idx + offset, y, width, label=col)
    ax.set_xticks(idx)
    ax.set_xticklabels(x, rotation=45, ha="right")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    plt.show()
