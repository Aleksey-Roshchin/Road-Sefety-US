import re
import numpy as np
import pandas as pd
from src.data_loader import load_orifinal_data_csv
import src.constants as consts

# Functions
def cities_count(df, num_rows=consts.NUM_ROWS, cities=None):
    if cities is None:
        #df_processed = df.groupby('City')['City'].count().sort_values(ascending=False).head(num_rows)
        df_processed = df['City'].value_counts().head(num_rows)
    else:
        df_processed = df[df['City'].isin(cities)].groupby('City')['City'].count().head(num_rows).sort_values(by='City', ascending=False)
    return df_processed