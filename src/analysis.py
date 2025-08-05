import re
import numpy as np
import pandas as pd
from src.data_loader import load_orifinal_data_csv
import src.constants as consts

# Functions
def count_by_cities(df: pd.DataFrame, num_rows=consts.NUM_ROWS, cities=None) -> pd.DataFrame:
    if cities is None:
        df_processed = df['City'].value_counts().head(num_rows).reset_index()
        df_processed.columns = ['City', 'Count']
    else:
        df_processed = df[df['City'].isin(cities)].groupby('City')['City'].count().head(num_rows).sort_values(by='City', ascending=False)
        df_processed.columns = ['City', 'Count']
    return df_processed