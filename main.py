import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import src.interface.user_interface as ui
import os, sys
from src.constants     import *
from src.data_loader   import *
from src.analysis      import *
from src.visualization import *
import pandas as pd
# df_original = pd.read_csv('data/processed/first_1000_rows.csv')
from src.preprocessing import base_preprocess_datetime
import time
import src.preprocessing as prepro
from src.constants import  CSV
from src.data_loader import load_orifinal_data_csv

#df_original = load_orifinal_data_csv()
df_original = pd.read_csv('data/processed/first_1000_rows.csv')
df_processed = prepro.object_columns_to_category(df_original, columns= ['City'])

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
if os.name == 'nt':
    os.system('chcp 65001 > nul')

def load_first_1000() -> pd.DataFrame:
    df = pd.read_csv(CSV, nrows=1000)
    df = base_preprocess_datetime(df, drop_last_year=False)
    df = feat(df)
    return df

def load_full() -> pd.DataFrame:
    df = ld(CSV)
    df = feat(df)
    return df


def main(df):
    ui.enable_utf8()
    ui.clear()
    ui.print_logo_centered(ui.PROGRAM_LOGO)
    ui.main_menu(df)


if __name__ == "__main__":
    main(df_processed)
    # df = load_first_1000()
    df = load_full()
    main(df)
