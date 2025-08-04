import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import src.interface.user_interface as ui
import time
from datetime import datetime
from src.constants import PROGRAM_LOGO, CSV
from src.data_loader import load_orifinal_data_csv

df_original = load_orifinal_data_csv()

def main(df):
    ui.clear()
    ui.print_logo_centered(PROGRAM_LOGO)
    ui.main_menu(df)


if __name__ == "__main__":
    main(df_original)