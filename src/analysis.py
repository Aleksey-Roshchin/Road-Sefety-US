import re
import numpy as np
import pandas as pd
from src.data_loader import load_orifinal_data_csv
import src.constants as consts
import src.preprocessing as prepro

# Functions
def count_by_cities(df: pd.DataFrame, num_rows=consts.NUM_ROWS, cities=None) -> pd.DataFrame:
    if cities is None:
        df_processed = df['City'].value_counts().head(num_rows).reset_index()
        df_processed.columns = ['City', 'NumOfAccidents']
    else:
        df_processed = df[df['City'].isin(cities)].groupby('City')['City'].count().head(num_rows).sort_values(by='City', ascending=False)
        df_processed.columns = ['City', 'NumOfAccidents']
    prepro.set_index_starting_from_one(df_processed)
    return df_processed


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
    df_processed['Year'] = df_processed['Year'].astype(str)     # To display the year as discret value when plot
    return df_processed


def city_accidents_count_by_year(df: pd.DataFrame, num_rows=consts.NUM_ROWS, city='new york') -> pd.DataFrame:
    df_processed = pd.DataFrame({
        "City": df['City'],
        'Year': pd.to_datetime(df['Start_Time']).dt.year
    })
    df_processed = df_processed[df['City'] == city]
    df_processed = df_processed.groupby('Year')['City'].count().reset_index()
    df_processed.columns = ['Year', 'NumAccidents']
    prepro.set_index_starting_from_one(df_processed)
    df_processed['Year'] = df_processed['Year'].astype(str)     # To display the year as discret value when plot
    return df_processed


def city_dangerous_streets(df: pd.DataFrame, city: str,  year: int, num_rows=consts.NUM_ROWS) -> pd.DataFrame:
    df_processed = pd.DataFrame({
        "City": df['City'],
        "Street": df['Street'],
        "Year": pd.to_datetime(df['Start_Time'].dt.year)
    })
    df_processed = df_processed[(df['City'] == city) | (df['Street'] == year)]
    df_processed = df_processed.groupby('').groupby('Year')['City'].count().reset_index()
    prepro.set_index_starting_from_one(df_processed)
    return df_processed
