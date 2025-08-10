import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import src.interface.user_interface as ui
import time
import src.preprocessing as prepro
from src.constants import  CSV
from src.data_loader import load_orifinal_data_csv

#df_original = load_orifinal_data_csv()
df_original = pd.read_csv('data/processed/first_1000_rows.csv')
df_processed = prepro.object_columns_to_category(df_original, columns=['City'])

def main(df):
    # print(df_processed.info())
    # print(df_processed['City'].head())
    # ui.press_to_continue()
    ui.clear()
    ui.print_logo_centered(ui.PROGRAM_LOGO)
    ui.main_menu(df)


if __name__ == "__main__":
    main(df_processed)