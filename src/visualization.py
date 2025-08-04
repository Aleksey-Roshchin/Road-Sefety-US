import matplotlib.pyplot as plt
import pandas as pd

def plot_corr(corr: pd.DataFrame):
    plt.figure(figsize=(12, 9), dpi=200)
    plt.imshow(corr, vmin=-1, vmax=1)
    plt.xticks(range(len(corr)), corr.columns, rotation=90, fontsize=6)
    plt.yticks(range(len(corr)), corr.index, fontsize=6)
    plt.colorbar()
    plt.tight_layout()
    plt.show()