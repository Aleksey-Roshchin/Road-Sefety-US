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
    ui.enable_utf8()
    ui.clear()
    ui.print_logo_centered(ui.PROGRAM_LOGO)
    ui.main_menu(df)

if __name__ == "__main__":
    # df = load_first_1000()
    df = load_full()
    main(df)
