import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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



