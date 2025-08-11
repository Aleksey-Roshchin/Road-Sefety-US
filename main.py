import os, sys
import pandas as pd
from src.interface import user_interface as ui
from src.constants import CSV
from src.data_loader import ld
from src.analysis import feat
from src.preprocessing import base_preprocess_datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
if os.name == 'nt':
    os.system('chcp 65001 > nul')

# df_original = load_orifinal_data_csv()
# df_original = pd.read_csv('data/processed/first_1000_rows.csv')
# df_processed = prepro.object_columns_to_category(df_original, columns=['City'])


def load_first_1000() -> pd.DataFrame:
    df = pd.read_csv(CSV, nrows=1000)
    df = base_preprocess_datetime(df)
    df = feat(df)
    return df

def load_full() -> pd.DataFrame:
    df = ld(CSV)
    df = base_preprocess_datetime(df)
    df = feat(df)
    return df

def main(df: pd.DataFrame):
    # print(df_processed.info())
    # print(df_processed['City'].head())
    # ui.press_to_continue()
    ui.enable_utf8()
    ui.clear()
    ui.print_logo_centered(ui.PROGRAM_LOGO)
    ui.main_menu(df)

if __name__ == "__main__":
    # df = load_first_1000()
    # main(df_processed)
    df = load_full()
    main(df)
